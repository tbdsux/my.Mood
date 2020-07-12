from dotenv import load_dotenv
import os

load_dotenv()

# this is the main config file
class App_Config:
    SECRET_KEY = "8a0e07496b187b1e478119fea6b8e80a"
    SEND_FILE_MAX_AGE_DEFAULT = 0
    CSRF_ENABLED = True
    TESTING = False
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")


class DevConfig(App_Config):
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:admin@localhost/myMood"
    DEVELOPMENT = True


class ProdConfig:
    SECRET_KEY = "8a0e07496b187b1e478119fea6b8e80a"
    SEND_FILE_MAX_AGE_DEFAULT = 0
    CSRF_ENABLED = True
    TESTING = False
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = "ima.boringdude@gmail.com"
    MAIL_PASSWORD = "Lecaj123!"
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
