# -*- coding: utf-8 -*-
"""
    Pytest config file
"""

import pytest
from sms import create_app

@pytest.fixture(scope="session")
def app():
    """Fixture for pytest-flask plugin"""
    app = create_app("testing")
    return app
