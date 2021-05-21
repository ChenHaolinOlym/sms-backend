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

