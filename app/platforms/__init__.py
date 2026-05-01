from flask import Blueprint
bp = Blueprint("platforms", __name__)
from app.platforms import views, models  # noqa: E402,F401
