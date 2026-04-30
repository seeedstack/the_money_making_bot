import json
import os
from flask import request, redirect, url_for, render_template_string
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.auth import bp
from app.auth.models import DashboardUser
from app.messages import AppMessages
from config.settings import settings

LOGIN_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>The Bot — Login</title>
<style>*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,sans-serif;background:#f5f5f5;color:#333}
.box{max-width:400px;margin:80px auto;padding:32px;background:white;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.1)}
h1{font-size:24px;margin-bottom:20px;text-align:center}
label{display:block;font-size:13px;font-weight:600;margin-bottom:4px}
input{width:100%;padding:9px 11px;border:1px solid #ddd;border-radius:4px;font-size:14px;margin-bottom:14px}
.btn{width:100%;padding:11px;background:#2563eb;color:white;border:none;border-radius:4px;font-size:15px;cursor:pointer}
.btn:hover{background:#1d4ed8}
.err{padding:8px;background:#fee2e2;color:#b91c1c;border-radius:4px;margin-bottom:14px;font-size:14px;text-align:center}
</style></head><body>
<div class="box"><h1>🤖 The Bot</h1>
{% if error %}<div class="err">{{ error }}</div>{% endif %}
<form method="POST"><label>Username</label><input name="username" required autofocus>
<label>Password</label><input type="password" name="password" required>
<button class="btn">Sign In</button></form></div></body></html>"""

CHANGE_PASSWORD_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Change Password</title>
<style>*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,sans-serif;background:#f5f5f5;color:#333}
.box{max-width:400px;margin:80px auto;padding:32px;background:white;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.1)}
h1{font-size:20px;margin-bottom:20px}
label{display:block;font-size:13px;font-weight:600;margin-bottom:4px}
input{width:100%;padding:9px 11px;border:1px solid #ddd;border-radius:4px;font-size:14px;margin-bottom:14px}
.btn{width:100%;padding:11px;background:#2563eb;color:white;border:none;border-radius:4px;font-size:15px;cursor:pointer}
.msg{padding:8px;border-radius:4px;margin-bottom:14px;font-size:14px;text-align:center}
.err{background:#fee2e2;color:#b91c1c}.ok{background:#dcfce7;color:#15803d}
a{display:block;text-align:center;margin-top:14px;font-size:13px;color:#6b7280}
</style></head><body>
<div class="box"><h1>Change Password</h1>
{% if error %}<div class="msg err">{{ error }}</div>{% endif %}
{% if success %}<div class="msg ok">{{ success }}</div>{% endif %}
<form method="POST"><label>Current Password</label><input type="password" name="current" required>
<label>New Password</label><input type="password" name="new" required minlength="8">
<label>Confirm</label><input type="password" name="confirm" required>
<button class="btn">Update</button></form>
<a href="/">← Dashboard</a></div></body></html>"""


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template_string(LOGIN_HTML)
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    if (username.lower() == settings.dashboard_username.lower()
            and check_password_hash(settings.dashboard_password_hash, password)):
        login_user(DashboardUser())
        return redirect(url_for("index"))
    return render_template_string(LOGIN_HTML, error=AppMessages.INVALID_CREDENTIALS), 401


@bp.route("/logout", methods=["POST"])
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "GET":
        return render_template_string(CHANGE_PASSWORD_HTML)
    current = request.form.get("current", "")
    new_pw = request.form.get("new", "")
    confirm = request.form.get("confirm", "")
    if not check_password_hash(settings.dashboard_password_hash, current):
        return render_template_string(CHANGE_PASSWORD_HTML, error=AppMessages.WRONG_CURRENT_PASSWORD), 400
    if len(new_pw) < 8:
        return render_template_string(CHANGE_PASSWORD_HTML, error=AppMessages.PASSWORD_TOO_SHORT), 400
    if new_pw != confirm:
        return render_template_string(CHANGE_PASSWORD_HTML, error=AppMessages.PASSWORDS_DO_NOT_MATCH), 400
    hashed = generate_password_hash(new_pw)
    creds_path = DashboardUser.creds_file_path()
    os.makedirs(os.path.dirname(creds_path), exist_ok=True)
    with open(creds_path, "w") as f:
        json.dump({"password_hash": hashed}, f)
    settings.dashboard_password_hash = hashed
    return render_template_string(CHANGE_PASSWORD_HTML, success=AppMessages.PASSWORD_UPDATED)
