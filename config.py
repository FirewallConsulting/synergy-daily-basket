import os


class Config:
    DEBUG = os.environ.get("DEBUG", False)
    SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///db.sqlite3")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FOODBASKET_API_URL = os.environ.get("FOODBASKET_API_URL")
    RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
    FLASK_RUN_PORT = os.environ.get("FLASK_RUN_PORT", 7000)

    # Celery configuration
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
    CELERY_RESULT_BACKEND = os.environ.get(
        "CELERY_RESULT_BACKEND", "redis://redis:6379/0"
    )
    CELERY_TIMEZONE = "America/Paramaribo"
    CELERY_ENABLE_UTC = True
