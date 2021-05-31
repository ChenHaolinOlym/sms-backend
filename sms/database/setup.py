# -*- coding: utf-8 -*-
"""
    Database base setup when no database exist
"""
from flask import current_app
import logging, json
from flask_sqlalchemy import SQLAlchemy
from .model import (
    Group,
    Part,
    Instrument,
    Event,
    Piece,
    Instrumentation,
    File,
    Transpose
)

def create_everything(db:SQLAlchemy) -> None:
    logger = logging.getLogger(__name__)
    with current_app.app_context():
        # Create database with model
        db.create_all()
        logger.info("Initiallize database")
        with open("sms/database/info.json", "r") as f:
            info = json.load(f)
        for groupName, parts in info.items():
            group = Group(name=groupName)
            for partName, instruments in parts.items():
                part = Part(name=partName)
                for instrumentName in instruments:
                    instrument = Instrument(name=instrumentName)
                    part.instruments.append(instrument)
                group.parts.append(part)
            db.session.add(group)
        db.session.commit()

    logger.info("Database created by config")