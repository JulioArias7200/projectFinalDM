"""
Dashboard blueprint package for ML Lab.
Modular Flask views and Jinja2 components.
"""
from flask import Blueprint

dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/dashboard/static"
)

from . import routes  # noqa: E402, F401
