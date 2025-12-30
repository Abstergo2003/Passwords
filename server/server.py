from flask import Flask, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix

# import threading
import os

# ENV Variables
from dotenv import load_dotenv


from modules.tools import (
    bcrypt,
)

# routes
from routes.add_routes import add_routes
from routes.update_routes import update_routes
from routes.get_routes import get_routes
from routes.delete_routes import delete_routes
from routes.authenticate_routes import authenticate_routes
from routes.mailbox_routes import mailbox_routes

load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY", "wad798!@wfttu89#lol")
ENABLE_BURNER_MAIL_SERVICE = os.getenv("ENABLE_BURNER_MAIL_SERVICE", "1")
WEBPANEL = os.getenv("WEBPANEL", "0")


app = Flask("Passwords Vault")
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

bcrypt.init_app(app)

app.register_blueprint(authenticate_routes)

app.register_blueprint(add_routes)

app.register_blueprint(update_routes)

app.register_blueprint(get_routes)

app.register_blueprint(delete_routes)


@app.route("/debug-ip")
def debug_ip():
    # 1. To powinno być Prawdziwe IP (dzięki ProxyFix)
    ip_flask = request.remote_addr

    # 2. To jest surowy nagłówek, który przysłał Nginx
    ip_header = request.headers.get("X-Forwarded-For", "Brak nagłówka")

    # 3. Pełna lista nagłówków (do głębokiej analizy)
    headers = dict(request.headers)

    # Wypisujemy do logów konsoli (z flush=True dla Dockera)
    print(f"--- DEBUG IP ---", flush=True)
    print(f"Remote Addr (Flask): {ip_flask}", flush=True)
    print(f"X-Forwarded-For:     {ip_header}", flush=True)
    print(f"----------------", flush=True)

    return jsonify(
        {"ip_flask_sees": ip_flask, "raw_header": ip_header, "all_headers": headers}
    )


if ENABLE_BURNER_MAIL_SERVICE == "1":
    app.register_blueprint(mailbox_routes)


if __name__ == "__main__":
    app.run(debug=False, port=5000, host="0.0.0.0", threaded=True)
