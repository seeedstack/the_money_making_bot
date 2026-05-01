from flask import Blueprint
bp = Blueprint("stats", __name__)
from app.stats import views  # noqa: E402,F401
