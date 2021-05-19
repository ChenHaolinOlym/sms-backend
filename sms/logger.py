# -*- coding: utf-8 -*-
"""
    Configure all the loggers in the project
"""

from flask import Flask
from logging.config import dictConfig

def init_logger(app:Flask) -> None:
    """Init the logger with the app instance

    :param app: The instance of the Flask app
    """
    with app.app_context():
        file = app.config["LOG_FILE"]
        level =  app.config["LOG_LEVEL"]
        maxBytes =  app.config["MAXBYTES"]
        backupCount =  app.config["BACKUPCOUNT"]

    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "incremental": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s"
            }
        },
        "handlers": {
            "file": {
                "level": level,
                "filename": file,
                "formatter": "default",
                "class": "logging.handlers.RotatingFileHandler",
                "maxBytes": maxBytes,
                "backupCount": backupCount
            },
            "console": {
                "level": level,
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout"
            }
        },
        "loggers": {
            "werkzeug": {
                "handlers": ["file"],
                "level": level,
                "propagate": True
            },
            "sms": {
                "handlers": ["file", "console"],
                "level": level,
                "propagate": True
            }
        }
    })
