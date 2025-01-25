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
            broker_url="redis://redis",
            result_backend="redis://redis",
            task_ignore_result=True,
            beat_schedule={
                "run-daily-sales-data-task": {
                    "task": "app.tasks.fetch_and_process_sales_data",
                    "schedule": crontab(hour=1, minute=0),
                },
                "hello-world": {
                    "task": "app.tasks.hello_world",
                    "schedule": crontab(minute="*/1"),
                },
            },
        ),
    )

    from app.routes import register_routes

    register_routes(app)
    celery_init_app(app)

    return app
