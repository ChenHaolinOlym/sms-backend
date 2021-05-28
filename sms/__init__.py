# -*- coding: utf-8 -*-
"""
    Init file. Contains the factory functions to initiallize the app
"""

from flask import Flask, render_template
from werkzeug.utils import import_string
import os, logging

from .logger import init_logger
from .database import db, create_everything
from .interface import api, register_blueprints

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
    else: # Production
        cfg = import_string('sms.config.ProductionConfigConfig')()
    app.config.from_object(cfg)

    # init loggers
    init_logger(app)
    logger = logging.getLogger(__name__)

    # initiallize database
    db.init_app(app)

    # init interface
    api.init_app(app)
    register_blueprints()

    # Check whether files folder exists
    if not os.path.isdir(app.config["FILES_DIR"]):
        logger.warning("No file folder is found")
        os.mkdir(app.config["FILES_DIR"])
        logger.info(f'Create new file folder at {app.config["FILES_DIR"]}')

    # Check whether database exists
    if not os.path.exists(os.path.join("sms", app.config['DB_FILE'])) and not app.config['TESTING']:
        app.app_context().push()
        create_everything(db)

    # Base Routes
    @app.get('/')
    def index():
        return render_template("index.html")

    return app