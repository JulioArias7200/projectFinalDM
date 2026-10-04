import sys
from pathlib import Path
from flask import Flask, redirect, url_for

# Permite ejecutar desde cualquier carpeta
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dashboard.routes import dashboard_bp

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-key-mllab-analytics-2026"
app.register_blueprint(dashboard_bp, url_prefix="/dashboard")


@app.route("/")
def index():
    return redirect(url_for("dashboard.index"))


if __name__ == "__main__":
    app.run(debug=True)
