import os


class Config:
    DEBUG = os.environ.get("DEBUG", False)
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND")
    FOODBASKET_API_URL = os.environ.get("FOODBASKET_API_URL")
    RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
    FLASK_RUN_PORT = os.environ.get("FLASK_RUN_PORT")
