from flask import Flask, render_template

from app.config import Config
from app import db
from app.routes.chat import chat_bp
from app.routes.conversations import conversations_bp
from app.routes.health import health_bp
from app.routes.plans import plans_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    if isinstance(config_class, dict):
        app.config.from_object(Config)
        app.config.from_mapping(config_class)
    else:
        app.config.from_object(config_class)

    db.init_app(app)
    with app.app_context():
        db.init_db()

    app.register_blueprint(chat_bp, url_prefix="/api")
    app.register_blueprint(conversations_bp, url_prefix="/api")
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(plans_bp, url_prefix="/api")

    @app.get("/")
    def index():
        return render_template("index.html")

    return app
