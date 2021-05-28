# -*- coding: utf-8 -*-
"""
    Configs of the system
"""
import os

class Config(object):
    # Custom configs
    # LOG
    LOG_FILE = "sms.log"
    LOG_LEVEL = "DEBUG"
    MAXBYTES = 1048576
    BACKUPCOUNT = 1
    # DB
    DB_FILE = "data.db"
    # FILE
    FILES_DIR = "files"

    # Flask configs
    DEBUG = False
    TESTING = False

    # Secret key from environ
    SECRET_KEY = os.environ.get("SECRET_KEY")

    # SqlAlchemy configs
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return f"sqlite:///{self.DB_FILE}"

    # API Configs
    API_TITLE = 'SMS'
    API_VERSION = 'v1'
    OPENAPI_VERSION = '3.0.2'

    # Api documentation configs
    OPENAPI_URL_PREFIX = "/api/description/"
    OPENAPI_JSON_PATH = "/openapi.json"
    OPENAPI_REDOC_PATH = "/redoc/"
    OPENAPI_REDOC_URL = "https://rebilly.github.io/ReDoc/releases/v1.22.3/redoc.min.js"
    OPENAPI_SWAGGER_UI_PATH = "/swaggerui/"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    OPENAPI_SWAGGER_UI_CONFIG = {'deepLinking': True, 'supportedSubmitMethods': ['get', 'post']}

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    LOG_FILE = "sms_test.log"
    DB_FILE = "test.db"
    FILES_DIR = "test_files"

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

