# -*- coding: utf-8 -*-
"""
    Api for Events
"""

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_smorest.error_handler import ErrorSchema

from .schemas import EventSchema, EventQuerySchema, EventCreateSchema, EventUpdateSchema, EventDeleteSchema
from ..database import db, Event, EventPiece

event_blp = Blueprint("eventsApi", __name__,
    url_prefix="/api/events", description="Api for Event")

@event_blp.route('/', endpoint="all")
class EventsApi(MethodView):

    @event_blp.arguments(EventQuerySchema, location="query")
    @event_blp.response(200, EventSchema(many=True))
    def get(self, args):
        """Get all events list"""
        return Event.query.filter_by(**args).all()

    @event_blp.arguments(EventCreateSchema, location="json")
    @event_blp.response(201, EventSchema)
    def post(self, args):
        """Create new event"""
        event = Event(name=args["name"])
        for piece in args["pieces"]:
            eventPiece = EventPiece(piece_id=piece["id"], order=piece["order"])
            event.events_pieces.append(eventPiece)
        db.session.add(event)
        db.session.commit()
        return event

    @event_blp.arguments(EventUpdateSchema, location="json")
    @event_blp.alt_response(404, ErrorSchema, description="Return 404 Not Found if the id provided is not valid")
    @event_blp.response(204)
    def put(self, args):
        """Update events (connot be used to create)"""
        event = Event.query.filter_by(id=args["id"])
        if event.first() == None:
            abort(404)
        else:
            pieces = args.pop("pieces", False)
            event.update(args)
            event = event.first()
            for event_piece in event.events_pieces:
                db.session.delete(event_piece)
            if pieces:
                for piece in pieces:
                    eventPiece = EventPiece(piece_id=piece["id"], order=piece["order"])
                    event.events_pieces.append(eventPiece)
        db.session.commit()
        return None

    @event_blp.arguments(EventDeleteSchema(many=True), location="json")
    @event_blp.response(204)
    def delete(self, args):
        """Delete events"""
        for event in args:
            event = Event.query.filter_by(id=event["id"]).first()
            for eventPiece in event.events_pieces:
                db.session.delete(eventPiece)
            db.session.delete(event)
        db.session.commit()
        return None

@event_blp.route("/<id>", endpoint="byid")
class EventsApiById(MethodView):

    @event_blp.arguments(EventQuerySchema, location="query")
    @event_blp.response(schema=EventSchema, status_code=200)
    def get(self, args, id):
        """Get event by id"""
        # param id in query string can overide id specified in original url
        id = args.pop("id", False) or id
        return Event.query.filter_by(id=id, **args).first()

    @event_blp.response(403, ErrorSchema)
    def post(self, id):
        """Forbidden"""
        return abort(403)

    @event_blp.response(403, ErrorSchema)
    def put(self, id):
        """Forbidden"""
        return abort(403)

    # @event_blp.arguments(EventDeleteSchema, location="json")
    @event_blp.alt_response(404, ErrorSchema, description="Return 404 Not Found if the id provided is not valid")
    @event_blp.response(204)
    # def delete(self, args, id):
    def delete(self, id):
        """Delete event by id"""
        # id = args.pop("id", False) or id
        event = Event.query.filter_by(id=id).first()
        if event:
            for eventPiece in event.events_pieces:
                db.session.delete(eventPiece)
            db.session.delete(event)
            db.session.commit()
            return None
        else:
            return abort(404)
