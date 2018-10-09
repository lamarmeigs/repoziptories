import json

from flask import make_response as make_flask_response


def make_response(content, status):
    return make_flask_response(
        json.dumps(content),
        status,
        {'Content-Type': 'application/json'}
    )
