# -*- coding: utf-8 -*-
"""
    Api for Groups, Parts and Instruments in one get
"""

from flask.views import MethodView
from flask_smorest import Blueprint, abort

from .schemas import InfoSchema
from ..database import Group, Part, Instrument

info_blp = Blueprint("infoApi", __name__,
    url_prefix="/api/info", description="Api for Group, Part and Instrument info")

@info_blp.route('/', endpoint="all")
class InfoApi(MethodView):

    @info_blp.response(200, InfoSchema)
    def get(self):
        groups = Group.query.all()
        parts = Part.query.all()
        instruments = Instrument.query.all()

        return dict(
            groups = groups,
            parts = parts,
            instruments = instruments
        )
