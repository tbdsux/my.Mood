from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_compress import Compress
from flask_assets import Environment, Bundle
from flask_caching import Cache

# import pylibmc
# from flask_session import Session
from myMood.config import ProdConfig
import os

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "users.user_login"
login_manager.login_message_category = "blue"
login_manager.session_protection = "strong"
mail = Mail()
compress = Compress()
cache = Cache()
assets = Environment()
# sess = Session()


def create_app(config_class=ProdConfig):
    app = Flask(__name__)
    app.config.from_object(ProdConfig)
    migrate = Migrate(app, db)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    compress.init_app(app)
    assets.init_app(app)
    # sess.init_app(app)

    css = Bundle("css/build.css")
    assets.register("main_css", css)

    cache.init_app(app, config={"CACHE_TYPE": "simple"})
    # Using Memcache
    # cache_servers = os.environ.get("MEMCACHIER_SERVERS")
    # if cache_servers == None:
    #     cache_servers = os.environ.get("MEMCACHIER_SERVERS")
    # else:
    #     cache_user = os.environ.get("MEMCACHIER_USERNAME") or ""
    #     cache_pass = os.environ.get("MEMCACHIER_PASSWORD") or ""
    #     cache.init_app(
    #         app,
    #         config={
    #             "CACHE_TYPE": "saslmemcached",
    #             "CACHE_MEMCACHED_SERVERS": cache_servers.split(","),
    #             "CACHE_MEMCACHED_USERNAME": cache_user,
    #             "CACHE_MEMCACHED_PASSWORD": cache_pass,
    #             "CACHE_OPTIONS": {
    #                 "behaviors": {
    #                     # Faster IO
    #                     "tcp_nodelay": True,
    #                     # Keep connection alive
    #                     "tcp_keepalive": True,
    #                     # Timeout for set/get requests
    #                     "connect_timeout": 2000,  # ms
    #                     "send_timeout": 750 * 1000,  # us
    #                     "receive_timeout": 750 * 1000,  # us
    #                     "_poll_timeout": 2000,  # ms
    #                     # Better failover
    #                     "ketama": True,
    #                     "remove_failed": 1,
    #                     "retry_timeout": 2,
    #                     "dead_timeout": 30,
    #                 }
    #             },
    #         },
    #     )
    #     app.config.update(
    #         SESSION_TYPE="memcached",
    #         SESSION_MEMCACHED=pylibmc.Client(
    #             cache_servers.split(","),
    #             binary=True,
    #             username=cache_user,
    #             password=cache_pass,
    #             behaviors={
    #                 # Faster IO
    #                 "tcp_nodelay": True,
    #                 # Keep connection alive
    #                 "tcp_keepalive": True,
    #                 # Timeout for set/get requests
    #                 "connect_timeout": 2000,  # ms
    #                 "send_timeout": 750 * 1000,  # us
    #                 "receive_timeout": 750 * 1000,  # us
    #                 "_poll_timeout": 2000,  # ms
    #                 # Better failover
    #                 "ketama": True,
    #                 "remove_failed": 1,
    #                 "retry_timeout": 2,
    #                 "dead_timeout": 30,
    #             },
    #         ),
    #     )

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
