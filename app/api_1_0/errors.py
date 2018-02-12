from flask import jsonify
from . import api
from app.exceptioins import ValidationError


def bad_request(message):
    response = jsonify({'error':'bad_request','message':message})
    response.status_code = 400
    return response

def unauthorized(message):
    response=jsonify({'error':'unauthorized','message':message})
    response.status_code = 401
    return response

def forbidden(message):
    response = jsonify({'error':'forbiddent','message':message})
    response.status_code = 403
    return response

@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])
