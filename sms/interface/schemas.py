# -*- coding: utf-8 -*-
"""
    All schemas for the interface
"""

from flask_marshmallow import Marshmallow
from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from flask_smorest.fields import Upload
from marshmallow import fields, Schema

from ..database import (
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

ma = Marshmallow()

class GroupSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Group
        load_instance = True
        include_fk = True
        include_relationships = False

    id = ma.auto_field(required=True)

class GroupQuerySchema(Schema):
    id = fields.Integer()
    name = fields.String()

class PartSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Part
        load_instance = True
        include_fk = True
        include_relationships = False
    
    id = ma.auto_field(required=True)

class PartQuerySchema(Schema):
    id = fields.Integer()
    name = fields.String()

class InstrumentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Instrument
        load_instance = True
        include_fk = True
        include_relationships = False

    id = ma.auto_field(required=True)

class InstrumentQuerySchema(Schema):
    id = fields.Integer()
    name = fields.String()

class InfoSchema(Schema):
    groups = fields.List(fields.Nested(GroupSchema))
    parts = fields.List(fields.Nested(PartSchema))
    instruments = fields.List(fields.Nested(InstrumentSchema))

class EventPieceSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = EventPiece
        load_instance = True
        include_fk = True
        include_relationships = False
    
    id = ma.auto_field(required=True)

class EventPieceCreateSchema(Schema):
    id = fields.Integer(required=True, error_messages={
        "required": "Id is required"
    })
    order = fields.Integer(required=True, error_messages={
        "required": "Order is required"
    })

class EventSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Event
        load_instance = True
        include_fk = True
        include_relationships = False

    id = ma.auto_field(required=True)
    events_pieces = fields.List(fields.Nested(EventPieceSchema(exclude=("event_id",))), data_key="pieces")

class EventQuerySchema(Schema):
    id = fields.Integer()
    name = fields.String()

class EventCreateSchema(Schema):
    name = fields.String(required=True, error_messages={
        "required": "Name is required"
    })
    pieces = fields.List(fields.Nested(EventPieceCreateSchema))

class EventUpdateSchema(Schema):
    id = fields.Integer(required=True, error_messages={
        "required": "Id is required"
    })
    name = fields.String(required=True, error_messages={
        "required": "Name is required"
    })
    pieces = fields.List(fields.Nested(EventPieceCreateSchema))

class EventDeleteSchema(Schema):
    id = fields.Integer(required=True, error_messages={
        "required": "Id is required"
    })

class InstrumentationSchema(SQLAlchemyAutoSchema):
    # TODO: Check the output of this schema
    class Meta:
        model = Instrumentation
        load_instance = True
        include_fk = False
        include_relationships = True

    id = ma.auto_field(required=True)

class InstrumentationCreateSchema(Schema):
    instrument_id = fields.Integer(required=True, error_messages={
        "required": "Instrument_id is required"
    })

class PieceSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Piece
        load_instance = True
        include_fk = True
        include_relationships = False

    id = ma.auto_field(required=True)
    instrumentations = fields.List(fields.Nested(InstrumentationSchema))

class PieceQuerySchema(Schema):
    id = fields.Integer()
    name = fields.String()
    author = fields.String()
    lyricist = fields.String()
    arranger = fields.String()
    opus = fields.Integer()
    type = fields.Integer()
    copyright_expire_date = fields.Date()
    created_time = fields.DateTime()

class PieceCreateSchema(Schema):
    name = fields.String(required=True, error_messages={
        "required": "Name is required"
    })
    author = fields.String()
    lyricist = fields.String()
    arranger = fields.String()
    opus = fields.Integer()
    type = fields.Integer()
    copyright_expire_date = fields.Date()
    group_ids = fields.List(fields.Integer(), required=True)
    instrumentations = fields.List(fields.Nested(InstrumentationCreateSchema))

class PieceUpdateSchema(Schema):
    id = fields.Integer(required=True, error_messages={
        "required": "Id is required"
    })
    name = fields.String(required=True, error_messages={
        "required": "Name is required"
    })
    author = fields.String()
    lyricist = fields.String()
    arranger = fields.String()
    opus = fields.Integer()
    type = fields.Integer()
    copyright_expire_date = fields.Date()
    group_ids = fields.List(fields.Integer())
    # instrumentations = fields.List(fields.Nested(InstrumentationCreateSchema))

class PieceDeleteSchema(Schema):
    id = fields.Integer(required=True, error_messages={
        "required": "Id is required"
    })

class TransposeSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Transpose
        load_instance = True
        include_fk = False
        include_relationships = True

    id = ma.auto_field(required=True)
    instrument = fields.Function(lambda obj: obj.instrument.name)

class TransposeCreateSchema(Schema):
    instrument_id = fields.Integer(required=True, error_messages={
        "required": "Instrument id is required"
    })

class FileSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = File
        load_instance = True
        include_fk = True
        include_relationships = False

    id = ma.auto_field(required=True)
    transpose = fields.Nested(TransposeSchema(exclude=("file",)))

class FileQuerySchema(Schema):
    hash_id = fields.String()
    format = fields.String()
    filename = fields.String()
    name = fields.String()
    type = fields.Integer()

class FileSingleCreateSchema(Schema):
    instrumentation_ids = fields.List(fields.Integer(), required=True, error_messages={
        "required": "An array of instrumentation ids should be provided"
    })
    name = fields.String(required=True, error_messages={
        "required": "Name of the file is required"
    })
    type = fields.Integer(required=True, error_messages={
        "required": "Type of the file is required"
    })
    transpose = fields.Nested(TransposeCreateSchema)

class MyList(fields.List):
    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(data, dict) and hasattr(data, 'getlist'):
            value = data.getlist(attr) # type: ignore
        return super()._deserialize(value, attr, data, **kwargs)

class FileCreateSchema(Schema):
    data = MyList(fields.String(), required=True, error_messages={
        "required": "An array of data of each file should be provided along with files"
    })

class FileUploadSchema(Schema):
    files = fields.List(Upload(required=True, error_messages={
        "required": "A file should be attached"
    }), data_key="files[]")

class FileUpdateSchema(Schema):
    pass

class FileDeleteSchema(Schema):
    hash_id = fields.String(required=True, error_messages={
        "required": "id is required when deleting data"
    })
