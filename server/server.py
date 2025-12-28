from flask import Flask

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

bcrypt.init_app(app)

app.register_blueprint(authenticate_routes)

app.register_blueprint(add_routes)

app.register_blueprint(update_routes)

app.register_blueprint(get_routes)

app.register_blueprint(delete_routes)

if ENABLE_BURNER_MAIL_SERVICE == "1":
    app.register_blueprint(mailbox_routes)


if __name__ == "__main__":
    app.run(debug=False, port=5000, host="0.0.0.0", threaded=True)
