from flask import jsonify
from app.messages import AppMessages


def bad_request(message: str = AppMessages.BAD_REQUEST):
    return jsonify({"error": message}), 400


def error_response(message: str, status: int = 500):
    return jsonify({"error": message}), status


def not_found(message: str):
    return jsonify({"error": message}), 404
