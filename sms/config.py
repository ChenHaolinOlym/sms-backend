# -*- coding: utf-8 -*-
"""
    Configs of the system
"""

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

