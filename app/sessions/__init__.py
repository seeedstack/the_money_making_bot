from flask import Blueprint
bp = Blueprint("sessions", __name__)
from app.sessions import views, models  # noqa: E402,F401
