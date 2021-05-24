# -*- coding: utf-8 -*-
"""
    Database test suite
"""

import pytest
from flask import Flask
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from hashids import Hashids

from sms.database import (
    Group,
    Part,
    Instrument,
    Event,
    EventPiece,
    Piece,
    Instrumentation,
    File,
    Transpose
)

class TestModel:
    def test_base_info(self, db:SQLAlchemy) -> None:
        # Inserts
        group = Group(name="test")
        part = Part(name="test")
        instrument = Instrument(name="test")
        group.parts.append(part)
        part.instruments.append(instrument)
        db.session.add(group)
        db.session.flush()
        # Queries
        test_group = Group.query.filter_by(name="test").first()
        test_part = Part.query.filter_by(name="test").first()
        test_instrument = Instrument.query.filter_by(name="test").first()
        # Asserts
        assert test_group.id == 1
        assert test_group.name == "test"
        assert test_part.id == 1
        assert test_part.name == "test"
        assert test_instrument.id == 1
        assert test_instrument.name == "test"
        db.session.rollback()

    def test_event_and_piece(self, db:SQLAlchemy) -> None:
        dt = datetime.now()
        event_args = {
            "name": "test"
        }
        piece_args = {
            "name": "test",
            "author": "test_author",
            "lyricist": "test_lyricist",
            "arranger": "test_arranger",
            "opus": "1",
            "copyright_expire_date": dt,
            "type": 0,
            "created_time": dt
        }
        # Inserts
        event = Event(**event_args)
        piece = Piece(**piece_args)
        instrumentation = Instrumentation(instrument_id=1)
        for i in range(10):
            event_piece = EventPiece(order=i)
            event.events_pieces.append(event_piece)
            piece.events_pieces.append(event_piece)
        piece.instrumentations.append(instrumentation)
        db.session.add(event)
        db.session.add(piece)
        db.session.flush()
        # Queries
        test_event = Event.query.filter_by(name="test").first()
        test_piece = Piece.query.filter_by(name="test").first()
        # Asserts
        assert test_event.id == 1
        assert test_event.name == "test"
        assert test_piece.id == 1
        assert test_piece.name == "test"
        assert test_piece.author == "test_author"
        assert test_piece.lyricist == "test_lyricist"
        assert test_piece.arranger == "test_arranger"
        assert test_piece.opus == "1"
        assert test_piece.copyright_expire_date == dt
        assert test_piece.type == 0
        assert test_piece.created_time == dt
        assert test_piece.instrumentations[0].id == 1
        for i in range(10):
            assert test_event.events_pieces[i].order == test_piece.events_pieces[i].order
        db.session.rollback()

    def test_file(self, db:SQLAlchemy, app:Flask) -> None:
        dt = datetime.now()
        file_args = {
            "created_time": dt,
            "format": "test_format",
            "name": "test",
            "type": "test_type"
        }
        # Inserts
        file = File(**file_args)
        transpose = Transpose()
        file.transpose = transpose
        db.session.add(file)
        db.session.flush()
        # Queries
        test_file = File.query.filter_by(name="test").first()
        # Asserts
        assert test_file.id == 1
        assert test_file.created_time == dt
        assert test_file.format == "test_format"
        assert test_file.name == "test"
        assert test_file.type == "test_type"
        assert test_file.hash_id == Hashids(app.config["SECRET_KEY"]).encode(test_file.id)
        db.session.rollback()

    def test_relationships(self, db:SQLAlchemy) -> None:
        dt = datetime.now()
        event_args = {
            "name": "test"
        }
        piece_args = {
            "name": "test",
            "author": "test_author",
            "lyricist": "test_lyricist",
            "arranger": "test_arranger",
            "opus": "1",
            "copyright_expire_date": dt,
            "type": 0,
            "created_time": dt
        }
        file_args = {
            "created_time": dt,
            "format": "test_format",
            "filename": "test_filename",
            "name": "test",
            "type": "test_type"
        }
        # Inserts
        group = Group(name="test")
        piece = Piece(**piece_args)
        event = Event(**event_args)
        instrumentation = Instrumentation(instrument_id=1)
        instrumentation.piece = piece
        file = File(**file_args)
        group.pieces.append(piece)
        group.events.append(event)
        instrumentation.files.append(file)
        db.session.add(group)
        db.session.add(instrumentation)
        db.session.flush()
        # Queries
        test_event = Event.query.first()
        test_piece = Piece.query.first()
        test_file = File.query.first()
        # Asserts
        assert test_event.groups[0] == test_piece.groups[0]
        assert test_file.instrumentations[0] == instrumentation
        # Inserts 2
        db.session.rollback()
        piece.groups.append(group)
        event.groups.append(group)
        file.instrumentations.append(instrumentation)
        db.session.add(group)
        db.session.add(instrumentation)
        db.session.flush()
        # Queries 2
        test_group = Group.query.first()
        test_instrumentation = Instrumentation.query.first()
        # Asserts 2
        assert test_group.events[0] == event
        assert test_group.pieces[0] == piece
        assert test_instrumentation.files[0] == file
        db.session.rollback()

if __name__ == "__main__":
    pytest.main()
