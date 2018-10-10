from distutils.util import strtobool

from flask import request

from application.api.common import make_response
from application.app import app
from clients import GithubClient, BitBucketClient
from clients.exceptions import (
    InvalidCredentialsError,
    RateLimitError,
    UnknownProfileError,
)
from config import config


@app.route('/v1/profile/<username>')
def get_merged_profiles_v1(username):
    profile = {}

    github_username = request.args.get('github_username', username)
    github_client = GithubClient(config['github_token'])
    try:
        profile['github'] = github_client.get_profile(github_username)
    except UnknownProfileError:
        profile['github'] = None
    except RateLimitError as error:
        return make_response({'error': str(error)}, 429)
    except InvalidCredentialsError as error:
        return make_response({'error': str(error)}, 401)

    bitbucket_username = request.args.get('bitbucket_username', username)
    is_team = bool(strtobool(request.args.get('bitbucket_team', 'true')))
    bitbucket_client = BitBucketClient()
    try:
        profile['bitbucket'] = bitbucket_client.get_profile(bitbucket_username, is_team=is_team)
    except UnknownProfileError:
        profile['bitbucket'] = None
    except RateLimitError as error:
        return make_response({'error': str(error)}, 429)

    return make_response(profile, 200)
