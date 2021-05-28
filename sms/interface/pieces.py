# -*- coding: utf-8 -*-
"""
    Api for Pieces
"""

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_smorest.error_handler import ErrorSchema
from werkzeug.utils import secure_filename

from .schemas import PieceSchema, PieceQuerySchema, PieceCreateSchema, PieceUpdateSchema, PieceDeleteSchema
from ..database import db, Piece, Group, Instrumentation
from ..utils import create_piece, delete_piece, rename_piece

piece_blp = Blueprint("piecesApi", __name__,
    url_prefix="/api/pieces", description="Api for Pieces")

@piece_blp.route("/", endpoint="all")
class PiecesApi(MethodView):

    @piece_blp.arguments(PieceQuerySchema, location="query")
    @piece_blp.response(200, PieceSchema(many=True))
    def get(self, args):
        """Get all pieces list"""
        return Piece.query.filter_by(**args).all()

    @piece_blp.arguments(PieceCreateSchema, location="json")
    @piece_blp.alt_response(409, ErrorSchema, description="Return 409 Conflict if the provided name is the same as an existing name")
    @piece_blp.response(201, PieceSchema)
    def post(self, args):
        """Create a new piece"""
        group_ids = args.pop("group_ids", None)
        instrumentations = args.pop("instrumentations", None)

        piece = Piece(**args)

        if create_piece(piece):
            # Relationship with Group
            for group_id in group_ids:
                group = Group.query.filter_by(id=group_id).first()
                piece.groups.append(group)

            # Instrumentations
            if instrumentations:
                for instrumentation in instrumentations:
                    instrumentation_instance = Instrumentation(instrument_id=instrumentation["instrument_id"])
                    piece.instrumentations.append(instrumentation_instance)
            db.session.add(piece)
            db.session.commit()
            return piece
        else:
            db.session.rollback()
            return abort(409)

    @piece_blp.arguments(PieceUpdateSchema, location="json")
    @piece_blp.alt_response(404, ErrorSchema, description="Return 404 Not Found if the id provided is not valid")
    @piece_blp.response(status_code=204)
    def put(self, args):
        """Update pieces (connot be used to create)"""
        # TODO: Complete update with instrumentation
        group_ids = args.pop("group_ids", None)
        piece = Piece.query.filter_by(id=args["id"])
        if piece.first() == None:
            return abort(404)
        else:
            original_name = piece.first().name
            if not secure_filename(original_name) == secure_filename(args["name"]):
                rename_piece(original_name, args["name"])
            piece.first().groups = []
            for group_id in group_ids:
                piece.first().groups.append(Group.query.filter_by(id=group_id).first())
            piece.update(args)
            db.session.commit()
            return None

    @piece_blp.arguments(PieceDeleteSchema(many=True), location="json")
    @piece_blp.alt_response(404, ErrorSchema, description="Return 404 Not Found if the id provided is not valid")
    @piece_blp.response(204)
    def delete(self, args):
        """Delete pieces from a list"""
        for arg in args:
            piece = Piece.query.filter_by(id=arg["id"]).first()
            if piece:
                for instrumentation in piece.instrumentations:
                    for file in instrumentation.files:
                        db.session.delete(file)
                    db.session.delete(instrumentation)
                db.session.delete(piece)
                db.session.commit()
                delete_piece(piece)
            else:
                return abort(404)
        return None

@piece_blp.route("/<id>", endpoint="byid")
class PiecesApiById(MethodView):

    @piece_blp.arguments(PieceQuerySchema, location="query")
    @piece_blp.response(200, PieceSchema)
    def get(self, args, id):
        # param id in query string can overide id specified in original url
        # But only the first result would be returned
        id = args.pop("id", False) or id
        return Piece.query.filter_by(id=id, **args).first()

    @piece_blp.response(403, ErrorSchema)
    def post(self, id):
        """Post is forbidden"""
        return abort(403)

    @piece_blp.response(403, ErrorSchema)
    def put(self, id):
        """Multi put is forbidden"""
        return abort(403)

    # @piece_blp.arguments(PieceDeleteSchema, location="json")
    @piece_blp.alt_response(404, ErrorSchema, description="Return 404 Not Found if the id provided is not valid")
    @piece_blp.response(204)
    # def delete(self, args, id):
    def delete(self, id):
        """Delete a whole piece"""
        # id = args.pop("id", False) or id
        piece = Piece.query.filter_by(id=id).first()
        if piece:
            for instrumentation in piece.instrumentations:
                for file in instrumentation.files:
                    db.session.delete(file)
                db.session.delete(instrumentation)
            db.session.delete(piece)
            db.session.commit()
            delete_piece(piece)
            return None
        else:
            return abort(404)
