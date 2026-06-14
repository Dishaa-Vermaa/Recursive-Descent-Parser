from flask import Flask, render_template, request, send_file
from parser_code import parser
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/parse', methods=['POST'])
def parse_expression():
    expression = request.form.get('expression')
    if not expression:
        return render_template('result.html', error="No input provided!")

    try:
        # Tokenize
        tokens = parser.tokenize(expression)

        # Parse
        p = parser.Parser(tokens)
        ast = p.parse_expr()

        # Evaluate
        result = parser.evaluate(ast)

        # Draw tree
        output_path = os.path.join('parser_code', 'expression_tree')
        parser.draw_tree(ast, output_path)

        # Return result page
        return render_template(
            'result.html',
            expression=expression,
            result=result,
            tokens=tokens[:-1],
            image_path='parser_code/expression_tree.png'
        )
    except Exception as e:
        return render_template('result.html', error=str(e))

@app.route('/image')
def serve_image():
    image_path = os.path.join('parser_code', 'expression_tree.png')
    return send_file(image_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
