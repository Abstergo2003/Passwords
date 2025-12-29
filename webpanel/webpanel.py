from flask import Flask, render_template, request, redirect, url_for
from modules.stats import get_dashboard_data, delete_user_fully
from modules.backups import create_backup, delete_backup, restore_backup, list_backups
from modules.scheduler import start_scheduler

# import threading
import os

# ENV Variables
from dotenv import load_dotenv

load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY", "wad798!@wfttu89#lol")


app = Flask("Passwords Vault Webpanel")
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "None"


@app.route("/dashboard", methods=["GET"])
def dashboard_view():

    stats = get_dashboard_data()
    backups = list_backups()
    return render_template("dashboard.html", stats=stats, backups=backups)


@app.route("/dashboard/delete_user", methods=["POST"])
def delete_user_route():

    user_id = request.form.get("user_id")

    if user_id:
        success = delete_user_fully(user_id)
        if success:
            print(f"Usunięto użytkownika: {user_id}")
        else:
            print("Błąd usuwania użytkownika")

    return redirect(url_for("dashboard_view"))


@app.route("/dashboard/backup/create", methods=["POST"])
def create_backup_route():
    # if not check_admin_auth(): return "Access Denied", 403
    success, msg = create_backup()
    # Tu można dodać Flash message
    return redirect(url_for("dashboard_view"))


@app.route("/dashboard/backup/delete", methods=["POST"])
def delete_backup_route():
    # if not check_admin_auth(): return "Access Denied", 403
    filename = request.form.get("filename")
    delete_backup(filename)
    return redirect(url_for("dashboard_view"))


@app.route("/dashboard/backup/restore", methods=["POST"])
def restore_backup_route():
    # if not check_admin_auth(): return "Access Denied", 403
    filename = request.form.get("filename")
    restore_backup(filename)
    return redirect(url_for("dashboard_view"))


if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    start_scheduler()

if __name__ == "__main__":
    app.run(debug=False, port=5050, host="0.0.0.0", threaded=True)
