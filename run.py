# -*- coding: utf-8 -*-
"""
    Entry file of the whole project
"""

from sms import create_app

app = create_app("development")

app.run(host="0.0.0.0", port=5000, threaded=True)
