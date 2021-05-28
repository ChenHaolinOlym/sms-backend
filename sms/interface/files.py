# -*- coding: utf-8 -*-
"""
    Api for Files
"""

import os
from flask import send_from_directory, current_app
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_smorest.error_handler import ErrorSchema
from sqlalchemy.orm import joinedload

from .schemas import FileSchema, FileQuerySchema, FileSingleCreateSchema, FileUploadSchema, FileCreateSchema, FileUpdateSchema, FileDeleteSchema
from ..database import db, File, Instrumentation, Transpose
from ..utils import save_file, delete_file, get_filename

file_blp = Blueprint("filesApi", __name__,
    url_prefix="/api/files", description="Api for Files")

@file_blp.route("/", endpoint="all")
class FilesApi(MethodView):

    @file_blp.arguments(FileQuerySchema, location="query")
    @file_blp.response(200, FileSchema(many=True, exclude=("id",)))
    def get(self, args):
        """Get all files list"""
        return File.query.filter_by(**args).all()

    @file_blp.arguments(FileUploadSchema, location="files")
    @file_blp.arguments(FileCreateSchema, location="form")
    @file_blp.alt_response(409, ErrorSchema, description="Return 409 Conflict if the provided name is the same as an existing name")
    @file_blp.response(201, FileSchema(many=True, exclude=("id",)))
    def post(self, file_args, args):
        """Upload File"""
        files = file_args["files"]
        args = args["data"][0]
        num_of_files = len(files)
        file_instances = []
        args = FileSingleCreateSchema(many=True).loads(args)

        for i in range(num_of_files):
            file = files[i]
            data = args[i]
            instrumentation_ids = data.pop("instrumentation_ids")
            transpose = data.pop("transpose") or None
            file_instance = File(**data)
            # Handling transpose
            if transpose:
                file_instance.transpose = Transpose(instrument_id=transpose["instrument_id"])

            # Handling instrumentation
            for instrumentation_id in instrumentation_ids:
                instrumentation = Instrumentation.query.filter_by(id=instrumentation_id).first()
                file_instance.instrumentations.append(instrumentation)

            # Handling format
            format = file.filename.split(".")[1]
            file_instance.format = format

            # Flush and save file
            db.session.add(file_instance)
            db.session.commit()
            if save_file(file_instance, file):
                new_file_instance = File.query.options(joinedload("transpose")).filter_by(id=file_instance.id).first()
                file_instances.append(new_file_instance)
            else:
                db.session.delete(File.query.order_by(File.id.desc()).first())
                return abort(409)

        return file_instances

    @file_blp.response(403, ErrorSchema)
    def put(self):
        """Put to update is forbidden, just delete then create"""
        abort(403)

    @file_blp.arguments(FileDeleteSchema(many=True), location="json")
    @file_blp.alt_response(404, ErrorSchema, description="Return 404 Not Found if the id provided is not valid")
    @file_blp.response(204)
    def delete(self, args):
        """Delete files in a list"""
        for arg in args:
            file = File.query.options(joinedload("instrumentations")).filter_by(hash_id=arg["hash_id"]).first()
            if file == None:
                return abort(404)
            else:
                # Handle transpose
                transpose = file.transpose
                db.session.delete(transpose)
                db.session.delete(file)

                if delete_file(file):
                    db.session.commit()
                    return None
                else:
                    return abort(404)


@file_blp.route("/<hash_id>", endpoint="byid")
class FilesApiById(MethodView):

    @file_blp.response(200)
    @file_blp.alt_response(404, ErrorSchema, description="Return 404 Not Found if the id provided is not valid")
    def get(self, hash_id):
        """Download file by hash_id"""
        file = File.query.filter_by(hash_id=hash_id).first()
        try:
            return send_from_directory(
                os.path.join(os.getcwd(), current_app.config["FILES_DIR"],
                file.instrumentations[0].piece.name), get_filename(file))
        except FileNotFoundError:
            return abort(404, message="File not found")

    @file_blp.response(403, ErrorSchema)
    def post(self, hash_id):
        """Forbidden"""
        abort(403)

    @file_blp.response(403, ErrorSchema)
    def put(self, hash_id):
        """Put to update is forbidden, just delete then create"""
        abort(403)

    # @file_blp.arguments(FileDeleteSchema)
    @file_blp.alt_response(404, ErrorSchema, description="Return 404 Not Found if the id provided is not valid")
    @file_blp.response(status_code=204)
    # def delete(self, args, hash_id):
    def delete(self, hash_id):
        """Delete file by id"""
        # hash_id = args.pop("hash_id", False) or hash_id
        file = File.query.options(joinedload("instrumentations")).filter_by(hash_id=hash_id).first()
        if file == None:
            return abort(404)
        else:
            # Handle transpose
            transpose = file.transpose
            db.session.delete(transpose)
            db.session.delete(file)

            if delete_file(file):
                db.session.commit()
                return None
            else:
                return abort(404)

