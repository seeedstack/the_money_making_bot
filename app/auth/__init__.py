from flask import Blueprint
bp = Blueprint("auth", __name__)
from app.auth import views, models  # noqa: E402,F401
