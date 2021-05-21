# -*- coding: utf-8 -*-
"""
    Pytest config file
"""

import pytest, os
from sms import create_app
from sms.database import db as original_db

@pytest.fixture(scope="session")
def app():
    """Fixture for pytest-flask plugin"""
    app = create_app("testing")
    return app

@pytest.fixture(scope="session")
def db(app, request):
    with app.app_context():
        # Create database with model
        original_db.create_all()

    def fin():
        '''Finalizer, execute when session ends'''
        with app.app_context():
            original_db.session.rollback()
            original_db.drop_all()
            original_db.session.close()
            os.remove(os.path.join("sms", app.config['DB_FILE']))

    request.addfinalizer(fin)
    return original_db

