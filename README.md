# Recursive Descent Parser — Run Instructions

This project contains a small Flask backend that parses and evaluates arithmetic expressions and generates a Graphviz expression tree image.

Two ways to run the project:

1) Recommended — Run the backend (Flask serves the frontend)

- Create and activate a Python virtual environment (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

- Install Python dependencies:

```powershell
pip install -r requirements.txt
```

- Install the Graphviz system package (required by the Python `graphviz` package):
- Windows: download and install from https://graphviz.org/download/ and add the installation `bin` folder to your `PATH`.

- Run the Flask app (this repository's `app.py` starts the server on port 5000):

```powershell
python app.py
```

- Open the app in your browser: http://127.0.0.1:5000

2) Alternative — Serve static frontend with Live Server (VS Code) and run backend separately

- Start the Flask backend as above (`python app.py`) so it listens on port 5000.
- Start VS Code Live Server to serve the static files (default port 5500).
- When using Live Server, the HTML form in `templates/index.html` will be served from port 5500 by Live Server. To make the form POST to the Flask backend on port 5000, update the form action to the full backend URL. Edit `templates/index.html` and change the form tag to:

```html
<form action="http://127.0.0.1:5000/parse" method="POST">
```

Notes and troubleshooting
- If you prefer not to edit the HTML, use the recommended approach and let Flask serve the templates directly — no Live Server required.
- If you see errors related to Graphviz (e.g., inability to generate the PNG), ensure the Graphviz binary is installed and on your `PATH`.
- If port 5000 is already in use, stop the service using it or change the port in `app.py` (modify `app.run(debug=True, port=<newport>)`).

Files added/used
- README: [README.md](README.md)
- Requirements: [requirements.txt](requirements.txt)

If you want, I can also update the `index.html` form action automatically or add a small note in `app.py` to make the backend URL configurable via an environment variable. Which would you prefer?
