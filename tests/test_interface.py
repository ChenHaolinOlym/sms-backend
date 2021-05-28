# -*- coding: utf-8 -*-
"""
    Database test suite
"""

from io import BytesIO
import pytest, json, os, shutil, re
from datetime import datetime
from _pytest.fixtures import SubRequest
from flask import Flask, url_for
from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy

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

class TestInfo:
    @pytest.fixture(scope="function", autouse=True)
    def prepare_db(self, db:SQLAlchemy, request:SubRequest):
        group = Group(name="test")
        part = Part(name="test")
        instrument = Instrument(name="test")
        part.group = group
        instrument.part = part
        db.session.add(group)
        db.session.flush()
        def fin():
            db.session.rollback()
        request.addfinalizer(fin)

    def test_get(self, client:FlaskClient):
        response = client.get(url_for('infoApi.all'))
        assert response.status_code == 200
        assert "test" in str(json.loads(response.data)["groups"])
        assert "test" in str(json.loads(response.data)["parts"])
        assert "test" in str(json.loads(response.data)["instruments"])

class TestEvent:
    @pytest.fixture(scope="function", autouse=True)
    def prepare_db(self, db:SQLAlchemy, request:SubRequest):
        event = Event(name="test")
        piece = Piece(name="test")
        eventPiece = EventPiece(order=1)
        event.events_pieces.append(eventPiece)
        piece.events_pieces.append(eventPiece)
        db.session.add(event)
        db.session.add(piece)
        db.session.commit()
        def fin():
            Event.query.delete()
            Piece.query.delete()
            EventPiece.query.delete()
            db.session.commit()
        request.addfinalizer(fin)

    def test_get(self, client:FlaskClient):
        response = client.get(url_for('eventsApi.all'))
        assert response.status_code == 200
        assert str(json.loads(response.data)) == """[{'id': 1, 'name': 'test', 'pieces': [{'id': 1, 'order': 1, 'piece_id': 1}]}]"""
        response = client.get(url_for('eventsApi.byid', id=1))
        assert response.status_code == 200
        assert str(json.loads(response.data)) == """{'id': 1, 'name': 'test', 'pieces': [{'id': 1, 'order': 1, 'piece_id': 1}]}"""

    def test_post(self, client:FlaskClient):
        data = {
            "name": "test2",
            "pieces": [{
                "id": 1,
                "order": 2
            }]
        }
        response = client.post(url_for('eventsApi.all'), json=data)
        assert response.status_code == 201
        assert str(json.loads(response.data)) == """{'id': 2, 'name': 'test2', 'pieces': [{'id': 2, 'order': 2, 'piece_id': 1}]}"""
        response = client.post(url_for('eventsApi.byid', id=1))
        assert response.status_code == 403
        response = client.get(url_for('eventsApi.all'))
        assert response.status_code == 200
        assert str(json.loads(response.data)) == """[{'id': 1, 'name': 'test', 'pieces': [{'id': 1, 'order': 1, 'piece_id': 1}]}, {'id': 2, 'name': 'test2', 'pieces': [{'id': 2, 'order': 2, 'piece_id': 1}]}]"""

    def test_put(self, client:FlaskClient):
        data = {
            "id": 1,
            "name": "test2",
            "pieces": [{
                "id": 1,
                "order": 3
            }]
        }
        response = client.put(url_for('eventsApi.all'), json=data)
        assert response.status_code == 204
        assert response.data.decode() == ""
        response = client.get(url_for("eventsApi.all"))
        assert response.status_code == 200
        assert str(json.loads(response.data)) == """[{'id': 1, 'name': 'test2', 'pieces': [{'id': 2, 'order': 3, 'piece_id': 1}]}]"""
        data["id"] = 2
        response = client.put(url_for("eventsApi.all"), json=data)
        assert response.status_code == 404

        response = client.put(url_for('eventsApi.byid', id=1))
        assert response.status_code == 403

    def test_delete(self, client:FlaskClient):
        data = {
            "id": 1
        }
        response = client.delete(url_for('eventsApi.all'), json=[data])
        assert response.status_code == 204
        response = client.get(url_for("eventsApi.all"))
        assert response.status_code == 200
        assert str(json.loads(response.data)) == "[]"
        data = {
            "name": "test2",
            "pieces": [{
                "id": 1,
                "order": 2
            }]
        }
        response = client.post(url_for('eventsApi.all'), json=data)
        assert response.status_code == 201
        response = client.delete(url_for("eventsApi.byid", id=1))
        assert response.status_code == 204
        assert response.data.decode() == ""

dt = datetime.now()

class TestPiece:
    @pytest.fixture(scope="function", autouse=True)
    def prepare_db(self, db:SQLAlchemy, request:SubRequest):
        group = Group(name="test")
        group2 = Group(name="test2")
        part = Part(name="test")
        instrument = Instrument(name="test")
        part.group = group
        instrument.part = part
        db.session.add(group)
        db.session.add(group2)
        db.session.commit()
        def fin():
            Piece.query.delete()
            Group.query.delete()
            Part.query.delete()
            Instrument.query.delete()
            db.session.commit()
        request.addfinalizer(fin)

    def test_post_delete(self, client:FlaskClient):
        # Test post
        data = {
            "name": "test",
            "author": "test_author",
            "lyricist": "test_lyricist",
            "arranger": "test_arranger",
            "opus": "1",
            "copyright_expire_date": dt.strftime("%Y-%m-%d"),
            "type": 0,
            "instrumentations": [{
                "instrument_id": 1
            }],
            "group_ids": [1]
        }
        response = client.post(url_for('piecesApi.all'), json=data)
        assert response.status_code == 201
        assert re.match(r"{'arranger': 'test_arranger', 'author': 'test_author', 'copyright_expire_date': .*, 'created_time': .*, 'id': 1, 'instrumentations': \[(?:{'files': \[.*\], 'id': 1, 'instrument': 1, 'piece': 1})*\], 'lyricist': 'test_lyricist', 'name': 'test', 'opus': 1, 'type': 0}", str(json.loads(response.data)))
        response = client.get(url_for('piecesApi.all'))
        assert response.status_code == 200
        assert re.match(r"[{'arranger': 'test_arranger', 'author': 'test_author', 'copyright_expire_date': .*, 'created_time': .*, 'id': 1, 'instrumentations': \[(?:{'files': \[.*\], 'id': 1, 'instrument': 1, 'piece': 1})*\], 'lyricist': 'test_lyricist', 'name': 'test', 'opus': 1, 'type': 0}]", str(json.loads(response.data)))
        response = client.post(url_for('piecesApi.all'), json=data)
        assert response.status_code == 409
        response = client.post(url_for('piecesApi.byid', id=1))
        assert response.status_code == 403

        # Test delete
        data = {
            "id": 1
        }
        response = client.delete(url_for('piecesApi.all'), json=[data])
        assert response.status_code == 204
        response = client.get(url_for("piecesApi.all"))
        assert response.status_code == 200
        assert str(json.loads(response.data)) == "[]"
        data = {
            "name": "test",
            "author": "test_author",
            "lyricist": "test_lyricist",
            "arranger": "test_arranger",
            "opus": "1",
            "copyright_expire_date": dt.strftime("%Y-%m-%d"),
            "type": 0,
            "instrumentations": [{
                "instrument_id": 1
            }],
            "group_ids": [1]
        }
        response = client.post(url_for('piecesApi.all'), json=data)
        assert response.status_code == 201
        response = client.delete(url_for("piecesApi.byid", id=1))
        assert response.status_code == 204
        assert response.data.decode() == ""

    def test_get_put(self, client:FlaskClient):
        data = {
            "name": "test",
            "author": "test_author",
            "lyricist": "test_lyricist",
            "arranger": "test_arranger",
            "opus": "1",
            "copyright_expire_date": dt.strftime("%Y-%m-%d"),
            "type": 0,
            "instrumentations": [{
                "instrument_id": 1
            }],
            "group_ids": [1]
        }
        response = client.post(url_for('piecesApi.all'), json=data)

        # Test get
        response = client.get(url_for('piecesApi.all'))
        assert response.status_code == 200
        assert re.match(r"\[{'arranger': 'test_arranger', 'author': 'test_author', 'copyright_expire_date': .*, 'created_time': .*, 'id': 1, 'instrumentations': \[(?:{'files': \[.*\], 'id': 1, 'instrument': 1, 'piece': 1})*\], 'lyricist': 'test_lyricist', 'name': 'test', 'opus': 1, 'type': 0}\]", str(json.loads(response.data)))
        response = client.get(url_for('piecesApi.byid', id=1))
        assert response.status_code == 200
        assert re.match(r"{'arranger': 'test_arranger', 'author': 'test_author', 'copyright_expire_date': .*, 'created_time': .*, 'id': 1, 'instrumentations': \[(?:{'files': \[.*\], 'id': 1, 'instrument': 1, 'piece': 1})*\], 'lyricist': 'test_lyricist', 'name': 'test', 'opus': 1, 'type': 0}", str(json.loads(response.data)))

        # Test put
        data = {
            "id": 1,
            "name": "test2",
            "author": "test_author2",
            "lyricist": "test_lyricist2",
            "arranger": "test_arranger2",
            "opus": "2",
            "copyright_expire_date": dt.strftime("%Y-%m-%d"),
            "type": 1,
            "group_ids": [2]
        }
        response = client.put(url_for('piecesApi.all'), json=data)
        assert response.status_code == 204
        assert response.data.decode() == ""
        response = client.get(url_for("piecesApi.all"))
        assert response.status_code == 200
        assert re.match(r"\[{'arranger': 'test_arranger2', 'author': 'test_author2', 'copyright_expire_date': .*, 'created_time': .*, 'id': 1, 'instrumentations': \[(?:{'files': \[.*\], 'id': 1, 'instrument': 1, 'piece': 1})*\], 'lyricist': 'test_lyricist2', 'name': 'test2', 'opus': 2, 'type': 1}\]", str(json.loads(response.data)))
        data["id"] = 2
        response = client.put(url_for("piecesApi.all"), json=data)
        assert response.status_code == 404

        response = client.put(url_for('piecesApi.byid', id=1))
        assert response.status_code == 403
        response = client.delete(url_for('piecesApi.byid', id=1))

class TestFile:

    @pytest.fixture(scope="function", autouse=True)
    def prepare_db(self, db:SQLAlchemy, app:Flask, request:SubRequest):
        group = Group(name="test")
        part = Part(name="test")
        instrument1 = Instrument(name="test1")
        instrument2 = Instrument(name="test2")
        piece = Piece(name="test")
        instrumentation1 = Instrumentation()
        instrumentation2 = Instrumentation()
        group.parts.append(part)
        instrumentation1.instrument = instrument1
        instrumentation2.instrument = instrument2
        part.instruments.extend([instrument1, instrument2])
        piece.instrumentations.extend([instrumentation1, instrumentation2])
        group.pieces.append(piece)
        db.session.add(piece)
        db.session.commit()
        os.mkdir(os.path.join(app.config["FILES_DIR"], "test"))
        def fin():
            db.drop_all()
            db.create_all()
            db.session.commit()
            shutil.rmtree(os.path.join(app.config["FILES_DIR"], "test"))
        request.addfinalizer(fin)

    def test_post_delete(self, client:FlaskClient):
        # Test post
        file = open("temp_test.temp", "ab+")
        data = {
            "data": '''[{
                "instrumentation_ids": [1],
                "name": "test",
                "type": 0,
                "transpose": {
                    "instrument_id": 2
                }
            }]''',
            "files[]": [(BytesIO(file.read()), 'temp.test')]
        }
        response = client.post(url_for("filesApi.all"), content_type="multipart/form-data", data=data)
        file.close()
        assert response.status_code == 201
        hash_id = json.loads(response.data)[0]["hash_id"]

        assert re.match(r"\[{'created_time': .*, 'format': 'test', 'hash_id': .*, 'name': 'test', 'transpose': {'id': 1, 'instrument': 'test2'}, 'type': 0}\]", str(json.loads(response.data)))
        file = open("temp_test.temp", "ab+")
        data = {
            "data": '''[{
                "instrumentation_ids": [1],
                "name": "test",
                "type": 0,
                "transpose": {
                    "instrument_id": 2
                }
            }]''',
            "files[]": [(BytesIO(file.read()), 'temp.test')]
        }
        response = client.post(url_for("filesApi.all"), content_type="multipart/form-data", data=data)
        file.close()
        assert response.status_code == 409
        response = client.post(url_for("filesApi.byid", hash_id="hash_id"))
        assert response.status_code == 403

        # Test delete
        data = {
            "hash_id": hash_id
        }
        response = client.delete(url_for("filesApi.all"), json=[data])
        assert response.status_code == 204
        file = open("temp_test.temp", "ab+")
        data = {
            "data": '''[{
                "instrumentation_ids": [1],
                "name": "test",
                "type": 0,
                "transpose": {
                    "instrument_id": 2
                }
            }]''',
            "files[]": [(BytesIO(file.read()), 'temp.test')]
        }
        response = client.post(url_for("filesApi.all"), content_type="multipart/form-data", data=data)
        file.close()
        hash_id = json.loads(response.data)[0]["hash_id"]
        response = client.delete(url_for("filesApi.byid", hash_id=hash_id))
        assert response.status_code == 204

        file.close()
        os.remove("temp_test.temp")

    def test_get_put(self, client:FlaskClient):
        # Test get
        # prepare
        file = open("temp_test.temp", "ab+")
        data = {
            "data": '''[{
                "instrumentation_ids": [1],
                "name": "test",
                "type": 0,
                "transpose": {
                    "instrument_id": 2
                }
            }]''',
            "files[]": [(BytesIO(file.read()), 'temp.test')]
        }
        response = client.post(url_for("filesApi.all"), content_type="multipart/form-data", data=data)
        file.close()
        hash_id = json.loads(response.data)[0]["hash_id"]
        # test
        response = client.get(url_for("filesApi.all"))
        assert response.status_code == 200
        assert re.match(r"\[{'created_time': .*, 'format': 'test', 'hash_id': .*, 'name': 'test', 'transpose': {'id': 1, 'instrument': 'test2'}, 'type': 0}\]", str(json.loads(response.data)))

        response = client.get(url_for("filesApi.byid", hash_id=hash_id))
        assert response.status_code == 200
        with open("temp_test.temp", "ab+") as file:
            assert response.data == file.read()

        # Let test_client close the file
        response = None

        response = client.delete(url_for("filesApi.byid", hash_id=hash_id))
        os.remove("temp_test.temp")
        # Test put
        response = client.put(url_for("filesApi.all"))
        assert response.status_code == 403
        response = client.put(url_for("filesApi.byid", hash_id="hash_id"))
        assert response.status_code == 403

if __name__ == "__main__":
    pytest.main()
