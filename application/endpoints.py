import json

from flask import Flask, make_response

from clients import GithubClient, BitBucketClient
from clients.exceptions import (
    InvalidCredentialsError,
    RateLimitError,
    UnknownProfileError,
)
from config import config


app = Flask(__name__.split('.')[0])


@app.route('/v1/profile/<username>')
def get_merged_profiles(username):
    profile = {}

    github_client = GithubClient(config['github_token'])
    try:
        profile['github'] = github_client.get_profile(username)
    except UnknownProfileError:
        profile['github'] = None
    except RateLimitError as error:
        return _make_response({'error': str(error)}, 429)
    except InvalidCredentialsError as error:
        return _make_response({'error': str(error)}, 401)

    bitbucket_client = BitBucketClient()
    try:
        profile['bitbucket'] = bitbucket_client.get_profile(username)
    except UnknownProfileError:
        profile['bitbucket'] = None
    except RateLimitError as error:
        return _make_response({'error': str(error)}, 429)

    return _make_response(profile, 200)


def _make_response(content, status):
    return make_response(
        json.dumps(content),
        status,
        {'Content-Type': 'application/json'}
    )
