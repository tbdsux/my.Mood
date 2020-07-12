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
    MAIL_USERNAME = "ima.boringdude@gmail.com"
    MAIL_PASSWORD = "Lecaj123!"


class DevConfig(App_Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///site.db"
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
    SQLALCHEMY_DATABASE_URI = "postgres://grvbhekhqlvgsa:2511c94f0b10581db1bab08ee8796c29ec03348cd221dc8d3e58ffe95bd8a0bf@ec2-52-202-146-43.compute-1.amazonaws.com:5432/dbpd7s2v4pejum"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
