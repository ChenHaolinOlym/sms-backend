# -*- coding: utf-8 -*-
"""
    Utils test suite
"""

import pytest, os
from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

from sms.utils import check_piece, check_file, get_filename, create_piece, save_file, delete_piece, delete_file
from sms.database import Piece, File, Instrumentation

class TestFileHandler:

    def test_get_filename(self, db:SQLAlchemy):
        """Test get_filename"""
        dt = datetime.now()
        file_args = {
            "created_time": dt,
            "format": "test_format",
            "name": "test",
            "type": 0
        }
        file = File(**file_args)
        db.session.add(file)
        db.session.flush()
        assert get_filename(file) == f"test_0_{file.hash_id}.test_format"
        db.session.rollback()

    def test_fs_manipulate_functions(self, db:SQLAlchemy):
        """Test function for check_piece, check_file, create_piece, save_file"""
        dt = datetime.now()
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
            "name": "test",
            "type": "test_type"
        }
        piece = Piece(**piece_args)
        instrumentation = Instrumentation(instrument_id=1)
        instrumentation.piece = piece
        file = File(**file_args)
        instrumentation.files.append(file)
        db.session.add(instrumentation)
        db.session.flush()
        assert check_piece(piece)
        assert check_file(file)
        
        temp_file = open("temp.temp_test", "ab+")
        fileStorage = FileStorage(temp_file)

        assert create_piece(piece)
        assert save_file(file, fileStorage)

        assert not check_piece(piece)
        assert not check_file(file)

        assert delete_file(file)
        assert check_file(file)
        assert not os.listdir(os.path.join(current_app.config["FILES_DIR"], secure_filename(piece.name)))

        assert delete_piece(piece)
        assert check_piece(piece)
        assert not os.listdir(current_app.config["FILES_DIR"])

        temp_file.close()
        os.remove("temp.temp_test")
