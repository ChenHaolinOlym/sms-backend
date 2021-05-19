# -*- coding: utf-8 -*-
"""
    Init file. Contains the factory functions to initiallize the app
"""

from flask import Flask, render_template
from werkzeug.utils import import_string
import os, logging

from .logger import init_logger

def create_app(mode="production") -> Flask:
    """Fatory function to initiallize the app
    
    :param mode: development, testing or production(default)
    """
    app = Flask(__name__)

    # Load configs
    if mode == "development":
        cfg = import_string('sms.config.DevelopmentConfig')()
    elif mode == "testing":
        cfg = import_string('sms.config.TestingConfig')()
    elif mode == "production":
        cfg = import_string('sms.config.ProductionConfigConfig')()
    app.config.from_object(cfg)

    # init loggers
    init_logger(app)
    logger = logging.getLogger(__name__)

    # Check files folders
    if not os.path.isdir(app.config["FILES_DIR"]):
        logger.warning("No file folder is found")
        os.mkdir(app.config["FILES_DIR"])
        logger.info(f'Create new file folder at {app.config["FILES_DIR"]}')

    # Base Routes
    @app.get('/')
    def index():
        return render_template("index.html")

    return app