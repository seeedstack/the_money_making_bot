from flask import Blueprint
bp = Blueprint("checks", __name__)
from app.checks import views, models  # noqa: E402,F401
