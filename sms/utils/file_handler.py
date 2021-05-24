# -*- coding: utf-8 -*-
"""
    Handlers for file input
"""

import os, shutil
from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from ..database import File, Piece

def check_piece(piece: Piece) -> bool:
    """Check whether a piece name has a duplicate
    
    Return True if no duplicate is found, return False if there's at least one duplicate"""
    with current_app.app_context():
        try:
            root, dirs, files = next(os.walk(current_app.config["FILES_DIR"], topdown=True))
            print(root)
            print(dirs)
            print(files)
            for dir in dirs:
                if secure_filename(piece.name) == dir:
                    return False
            return True
        except (IndexError, StopIteration):
            print("inExcept")
            return True

def check_file(info: File) -> bool:
    """Check whether a file name has a duplicate
    
    Return True if no duplicate is found, return False if there's at least one duplicate"""
    with current_app.app_context():
        try:
            root, dirs, files = next(os.walk(os.path.join(current_app.config["FILES_DIR"], secure_filename(info.instrumentations[0].piece.name)), topdown=True))
            for file in files:
                if get_filename(info) == file:
                    return False
            return True
        except (IndexError, StopIteration):
            return True

def get_filename(file: File) -> str:
    """Return the secure filename of the file"""
    return file.name + "_" + str(file.type) + "_" + file.hash_id + "." + file.format

def create_piece(piece: Piece) -> bool:
    """Create a piece folder according to the Piece instance"""
    if check_piece(piece):
        with current_app.app_context():
            os.mkdir(os.path.join(current_app.config["FILES_DIR"], secure_filename(piece.name)))
        return True
    else:
        return False

def save_file(info: File, file: FileStorage) -> bool:
    """Save File according to the File instance
    
    Return False if duplicate check failed, otherwise True"""
    if check_file(info):
        file.save(os.path.join(current_app.config["FILES_DIR"], info.instrumentations[0].piece.name, get_filename(info)))
        return True
    else:
        return False

def delete_piece(piece: Piece):
    """Delete the whole piece folder accoding to the Piece instance"""
    if not check_piece(piece):
        shutil.rmtree(os.path.join(current_app.config["FILES_DIR"], piece.name))
        return True
    else:
        return False

def delete_file(file: File):
    """Delet file accoding to the File instance"""
    if not check_file(file):
        os.remove(os.path.join(current_app.config["FILES_DIR"],
            file.instrumentations[0].piece.name, get_filename(file)))
        return True
    else:
        return False
