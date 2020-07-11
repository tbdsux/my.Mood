from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_compress import Compress
from flask_cache import Cache
from myMood.config import ProdConfig
import os

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "users.user_login"
login_manager.login_message_category = "blue"
mail = Mail()
compress = Compress()
cache = Cache()


def create_app(config_class=ProdConfig):
    app = Flask(__name__)
    app.config.from_object(ProdConfig)
    migrate = Migrate(app, db)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    compress.init_app(app)
    cache.init_app(cache)

    # Blueprints
    from myMood.users.routes import users
    from myMood.stories.routes import stories
    from myMood.main.routes import main
    from myMood.errors.handlers import errors

    # register blueprints
    app.register_blueprint(users)
    app.register_blueprint(stories)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app
