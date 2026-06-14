# Recursive Descent Parser with Graphical Expression Tree (Graphviz)
# Enhanced: strict error detection (no partial parsing), token positions, friendly messages

from dataclasses import dataclass
from typing import List, Optional
from graphviz import Digraph

# -----------------------
# TOKEN DEFINITION
# -----------------------
@dataclass
class Token:
    type: str
    value: Optional[str] = None
    pos: Optional[int] = None   # 1-based character index
    def __repr__(self):
        return f"{self.type}({self.value})@{self.pos}"

class ParserError(Exception):
    pass

# -----------------------
# LEXICAL ANALYZER
# -----------------------
def tokenize(text: str) -> List[Token]:
    tokens: List[Token] = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch.isspace():
            i += 1
            continue
        if ch.isdigit():
            start = i
            num = ch
            i += 1
            while i < len(text) and text[i].isdigit():
                num += text[i]
                i += 1
            tokens.append(Token("NUMBER", num, start+1))
            continue
        if ch in "+-*/()":
            token_type = {
                '+': 'PLUS', '-': 'MINUS',
                '*': 'MUL', '/': 'DIV',
                '(': 'LPAREN', ')': 'RPAREN'
            }[ch]
            tokens.append(Token(token_type, ch, i+1))
            i += 1
            continue
        raise ParserError(f"Invalid character '{ch}' at position {i+1}")
    tokens.append(Token("EOF", None, len(text)+1))
    return tokens

# -----------------------
# AST NODE DEFINITIONS
# -----------------------
@dataclass
class Number:
    value: int

@dataclass
class BinOp:
    left: object
    op: str
    right: object

# -----------------------
# PARSER IMPLEMENTATION
# -----------------------
class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def current(self) -> Token:
        return self.tokens[self.pos]

    def peek(self, offset=1) -> Token:
        idx = self.pos + offset
        return self.tokens[idx] if idx < len(self.tokens) else Token("EOF", None, self.current().pos+1)

    def eat(self, token_type: str):
        if self.current().type == token_type:
            self.pos += 1
        else:
            cur = self.current()
            raise ParserError(f"Syntax error at pos {cur.pos}: Expected '{token_type}', found '{cur.type}' ({cur.value})")

    def parse_expr(self):
        node = self.parse_term()
        while self.current().type in ("PLUS", "MINUS"):
            op = self.current().type
            self.eat(op)
            node = BinOp(node, op, self.parse_term())
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.current().type in ("MUL", "DIV"):
            op = self.current().type
            self.eat(op)
            node = BinOp(node, op, self.parse_factor())
        return node

    def parse_factor(self):
        tok = self.current()
        if tok.type == "NUMBER":
            # lookahead: if next meaningful token is LPAREN or NUMBER => missing operator
            next_tok = self.peek(1)
            if next_tok.type in ("NUMBER", "LPAREN"):
                raise ParserError(
                    f"Missing operator at pos {next_tok.pos}: token '{next_tok.type}' after a number. Did you mean '*' or '+'?"
                )
            self.eat("NUMBER")
            return Number(int(tok.value))

        # Parenthesized expression
        elif tok.type == "LPAREN":
            self.eat("LPAREN")
            node = self.parse_expr()
            if self.current().type != "RPAREN":
                cur = self.current()
                raise ParserError(f"Missing closing parenthesis at pos {cur.pos} (found '{cur.type}')")
            self.eat("RPAREN")
            # After a parenthesized group, check for implicit multiplication like ")("
            nxt = self.current()
            if nxt.type in ("NUMBER", "LPAREN"):
                raise ParserError(f"Missing operator at pos {nxt.pos}: '{nxt.type}' after ')'")
            return node

        else:
            raise ParserError(f"Unexpected token at pos {tok.pos}: '{tok.type}'")

    def parse(self):
        node = self.parse_expr()
        if self.current().type != "EOF":
            cur = self.current()
            # detailed token stream snippet
            stream = " ".join(f"{t.type}({t.value})@{t.pos}" for t in self.tokens if t.type != "EOF")
            raise ParserError(f"Extra tokens after valid expression starting at pos {cur.pos}: '{cur.type}({cur.value})'. Full tokens: {stream}")
        return node

# -----------------------
# AST EVALUATOR
# -----------------------
def evaluate(node):
    if isinstance(node, Number):
        return node.value
    elif isinstance(node, BinOp):
        left = evaluate(node.left)
        right = evaluate(node.right)
        if node.op == "PLUS": return left + right
        if node.op == "MINUS": return left - right
        if node.op == "MUL": return left * right
        if node.op == "DIV":
            if right == 0:
                raise ParserError("Division by zero")
            # Use float division if you prefer float results; original used integer //:
            return left // right
    else:
        raise ParserError("Invalid AST node")

# -----------------------
# GRAPHVIZ TREE GENERATOR
# -----------------------
def add_nodes_edges(dot, node, parent=None):
    if isinstance(node, Number):
        node_label = f"Number({node.value})"
    elif isinstance(node, BinOp):
        node_label = node.op
    else:
        return

    node_id = str(id(node))
    dot.node(node_id, node_label, shape="ellipse", style="filled", color="lightblue")

    if parent:
        dot.edge(parent, node_id)

    if isinstance(node, BinOp):
        add_nodes_edges(dot, node.left, node_id)
        add_nodes_edges(dot, node.right, node_id)

def draw_tree(ast, filename="expression_tree"):
    dot = Digraph(comment="Expression Tree", format='png')
    add_nodes_edges(dot, ast)
    dot.render(filename, cleanup=True)
    print(f"✅ Expression tree saved as {filename}.png")

# -----------------------
# MAIN PROGRAM
# -----------------------
def main():
    print("\n=== Recursive Descent Parser (strict mode) ===\n")
    expr = input("Enter an arithmetic expression: ").strip()
    if not expr:
        print("⚠️ Empty input. Please enter a valid expression.")
        return

    try:
        tokens = tokenize(expr)
        # show tokens except EOF
        print("\nTokens:", [str(t) for t in tokens if t.type != "EOF"])

        parser = Parser(tokens)
        ast = parser.parse()          # IMPORTANT: use parse() (enforces EOF)

        print("\nEvaluating...")
        result = evaluate(ast)
        print(f"✅ Result: {result}")

        print("\nGenerating expression tree image...")
        draw_tree(ast)

        print("\n✅ Done! Open 'expression_tree.png' to view the tree diagram.")

    except ParserError as e:
        # friendly, detailed parsing error — no tree generation or eval
        print(f"\n❌ Parsing Error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()

