# -*- coding: utf-8 -*-
"""
    Test routes
"""
import pytest

@pytest.mark.usefixtures('client_class')
class TestRoutes:
    """"""
    def test_baseRoute(self):
        """Test whether the base route '/' is served correctly"""
        response = self.client.get('/')
        assert response.status_code == 200
        assert type(response.data) == bytes
        assert response.data != ""
