# -*- coding: utf-8 -*-
"""
    SqlAlchemy models for database
"""

from flask_sqlalchemy import SQLAlchemy
from flask import current_app
from sqlalchemy import event
from datetime import datetime
from hashids import Hashids

db = SQLAlchemy()

# Models
# Middle Tables
# Groups & Pieces
groups_pieces = db.Table('groupsPieces',
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id'), primary_key=True, nullable=False),
    db.Column('piece_id', db.Integer, db.ForeignKey('pieces.id'), primary_key=True, nullable=False)
)

# Groups & Events
groups_events = db.Table('groupsEvents',
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id'), primary_key=True, nullable=False),
    db.Column('event_id', db.Integer, db.ForeignKey('events.id'), primary_key=True, nullable=False)
)

# Instrumentations & Files
instrumentations_files = db.Table('instrumentationsFiles',
    db.Column('instrumentation_id', db.Integer, db.ForeignKey('instrumentations.id'), primary_key=True),
    db.Column('file_id', db.Integer, db.ForeignKey('files.id'), primary_key=True, nullable=False)
)

# Tables
class Group(db.Model):
    """Model class for groups

    :column id: Primary Key
    :column name: Name of the group
    :relationship parts: Relationship with Parts, one-to-many, one end
    :relationship pieces: Relationship with pieces, many-to-many
    :relationship events: Relationship with events, many-to-many
    """
    __tablename__ = "groups"
    # Columns
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    # Relationships
    parts = db.relationship("Part", backref="group", lazy=True)
    pieces = db.relationship("Piece", secondary=groups_pieces, lazy="subquery", backref=db.backref("groups", lazy=True))
    events = db.relationship("Event", secondary=groups_events, lazy="subquery", backref=db.backref("groups", lazy=True))
    
    def __repr__(self) -> str:
        return str({
            "Table": "groups",
            "id": self.id,
            "name": self.name
        })

class Part(db.Model):
    """Model class for parts

    :column id: Primary Key
    :column name: Name of the part
    :column group_id: Foreign Key, id of Piece
    :relationship instruments: Relationship with instruments, one-to-many, one end
    """
    __tablename__ = "parts"
    # Columns
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    # Foreign Keys
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    # Relationships
    instruments = db.relationship("Instrument", backref="part", lazy=True)
    
    def __repr__(self) -> str:
        return str({
            "Table": "parts",
            "id": self.id,
            "name": self.name
        })

class Instrument(db.Model):
    """Model class for instruments

    :column id: Prinary Key
    :column name: Name of the instrument
    :column part_id: Foreign Key, id of part
    :relationship instrumentations: Relationship with instrumentations, one-to-many, one end
    :relationship transposes: Relationship with transposes, one-to-many, one end
    """
    __tablename__ = "instruments"
    # Columns
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    # Foreign Keys
    part_id = db.Column(db.Integer, db.ForeignKey("parts.id"), nullable=False)
    # Relationships
    instrumentations = db.relationship('Instrumentation', backref="instrument", lazy=True)
    transposes = db.relationship('Transpose', backref="instrument", lazy=True)

    def __repr__(self) -> str:
        return str({
            "Table": "instruments",
            "id": self.id,
            "name": self.name
        })

class Event(db.Model):
    """Model class for events

    :column id: Primary Key
    :column name: Name of the event
    :relationship groups: Relationship with groups, many-to-many
    :relationship events_pieces: Relationship with events_pieces, one-to-many, one end
    """
    __tablename__ = "events"
    # Columns
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    # Relationships
    events_pieces = db.relationship("EventPiece", backref="event", lazy=True)
    # groups_events many-to-many

    def __repr__(self) -> str:
        return str({
            "Table": "events",
            "id": self.id,
            "name": self.name
        })

class Piece(db.Model):
    """Model class for pieces

    :column id: Primary Key
    :column name: Name of the piece 
    :column author: Author of the piece 
    :column lyricist: Lyricist of the piece 
    :column arranger: Arranger of the piece
    :column opus: Opus of the piece
    :column type: Type of the piece
    :column copyright_expire_date: Copyright expire date of the piece 
    :column created_time: Piece's created time
    :relationship groups: Relationship with groups, many-to-many
    :relationship instrumentations: Relationship with instrumentations, one-to-many, one end
    :relationship events_pieces: Relationship with events_pieces, one-to-many, one end
    """
    __tablename__ = "pieces"
    # Columns
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    author = db.Column(db.Text)
    lyricist = db.Column(db.Text)
    arranger = db.Column(db.Text)
    opus = db.Column(db.Integer)
    type = db.Column(db.Integer, default=0)
    copyright_expire_date = db.Column(db.Date)
    created_time = db.Column(db.DateTime, default=datetime.now())
    # Relationships
    # groups_pieces many-to-many
    instrumentations = db.relationship("Instrumentation", backref="piece", lazy=True)
    events_pieces = db.relationship("EventPiece", backref="piece", lazy=True)

    def __repr__(self) -> str:
        return str({
            "Table": "pieces",
            "id": self.id,
            "name": self.name,
            "author": self.author,
            "lyricist": self.lyricist,
            "arranger": self.arranger,
            "opus": self.opus,
            "type": self.type,
            "copyright_expire_date": self.copyright_expire_date,
            "created_time": self.created_time,
            "modified_time": self.modified_time
        })

# Middle table for Events & Pieces
class EventPiece(db.Model):
    """Model class for the middle table of Events & Pieces

    :column id: Primary Key
    :column order: Order of the piece in an event
    :relationship events: Relationship with events, one-to-many, many end
    :relationship pieces: Relationship with pieces, one-to-many, many end
    """
    __tablename__ = "eventPiece"
    # Columns
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    order = db.Column(db.Integer, nullable=False)
    # Foreign Keys
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    piece_id = db.Column(db.Integer, db.ForeignKey('pieces.id'), nullable=False)
    # Relationships
    # events_events_pieces, one-to-many, many end
    # events_events_pieces, one-to-many, many end

    def __repr__(self) -> str:
        return str({
            "Table": "eventsPieces",
            "id": self.id,
            "order": self.order
        })

class Instrumentation(db.Model):
    """Model class for instrumentations

    :column id: Primary Key
    :column piece_id: Foreign Key, id of piece
    :column instrument_id: Foreign Key, id of instrument
    :relationship files: Relationship with files, many-to-many
    """
    __tablename__ = "instrumentations"
    # Columns
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    # Foreign Keys
    piece_id = db.Column(db.Integer, db.ForeignKey('pieces.id'), nullable=False)
    instrument_id = db.Column(db.Integer, db.ForeignKey('instruments.id'), nullable=False)
    # Relationships
    files = db.relationship("File", secondary=instrumentations_files, lazy="subquery", backref=db.backref("instrumentations", lazy=True))

    def __repr__(self) -> str:
        return str({
            "Table": "instrumentations",
            "id": self.id
        })

class File(db.Model):
    """Model class for files

    :column id: Primary Key
    :column hash_id: hash id for the file, generated with respect to id
    :column created_time: created time of the file
    :column format: file format (extention) of the file
    :column filename: file system storeage name of the file, often consisted by almost all attributes of File
    :column name: display name of the file, often consisted by instrument name+voice. e.g. Violin 1/Violin 2
    :column type: type of the file. e.g. original/revised
    :relationship transpose: Relationship with tranposes, one-to-one, nullable
    :relationship instrumentations: Relationship with instrumentations, many-to-many
    """
    __tablename__ = "files"
    # Columns
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    hash_id = db.Column(db.Text, index=True, default="", nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.now())
    format = db.Column(db.Text)
    filename = db.Column(db.Text)
    name = db.Column(db.String, nullable=False)
    type = db.Column(db.Integer, default=0)
    # Foreign Keys
    # Relationships
    # instrumentations_files many-to-many
    transpose = db.relationship("Transpose", backref="file", lazy=True, uselist=False)

    def __repr__(self) -> str:
        return str({
            "Table": "files",
            "id": self.id,
            "hash_id": self.hash_id,
            "created_time": self.created_time,
            "format": self.format,
            "filename": self.filename,
            "name": self.name,
            "type": self.type
        })

class Transpose(db.Model):
    """Model class for transposes

    :column id: Primary Key
    :column file_id: Foreign Key, the id of the file
    :column instrument_id: Foreign Key, the id of the instrument where the file is transposed from
    """
    __tablename__ = "transposes"
    # Columns
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    # Foreign Keys
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'))
    instrument_id = db.Column(db.Integer, db.ForeignKey('instruments.id'))

    def __repr__(self) -> str:
        return str({
            "Table": "transposes",
            "id": self.id
        })

# Hooks
@event.listens_for(File, 'after_insert')
def add_hash(mapper, connection, target):
    hashid = Hashids(current_app.config["SECRET_KEY"])
    target.hash_id = hashid.encode(target.id)
