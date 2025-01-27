from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate
from config import Config
from app.celery import celery_init_app
from celery.schedules import crontab

db = SQLAlchemy()
mail = Mail()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    app.config.from_mapping(
        CELERY=dict(
            broker_url=Config.CELERY_BROKER_URL,
            result_backend=Config.CELERY_RESULT_BACKEND,
            task_ignore_result=True,
            beat_schedule={
                "send_email": {
                    "task": "app.routes.send_email",
                    "schedule": crontab(hour=10, minute=00),
                },
            },
            include=["app.tasks"],
            timezone=Config.CELERY_TIMEZONE,
        ),
    )

    from app.routes import register_routes

    register_routes(app)
    celery_init_app(app)

    return app
