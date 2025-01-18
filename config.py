import os


class Config:
    DEBUG = os.environ.get("DEBUG", False)
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # MAIL_SERVER = os.environ.get("MAIL_SERVER")
    # MAIL_PORT = int(os.environ.get("MAIL_PORT"))
    # MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", False)
    # MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    # MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    # SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
    FOODBASKET_API_URL = os.environ.get("FOODBASKET_API_URL")
    RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
