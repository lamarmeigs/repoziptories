from distutils.util import strtobool

from flask import Flask, request

from application.helpers import make_response, merge_profiles
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
    github_username = request.args.get('github_username', username)
    github_client = GithubClient(config['github_token'])
    try:
        github_profile = github_client.get_profile(github_username)
    except UnknownProfileError:
        github_profile = None
    except RateLimitError as error:
        return make_response({'error': str(error)}, 429)
    except InvalidCredentialsError as error:
        return make_response({'error': str(error)}, 401)

    bitbucket_username = request.args.get('bitbucket_username', username)
    is_team = bool(strtobool(request.args.get('bitbucket_team', 'true')))
    bitbucket_client = BitBucketClient()
    try:
        bitbucket_profile = bitbucket_client.get_profile(
            bitbucket_username,
            is_team=is_team
        )
    except UnknownProfileError:
        bitbucket_profile = None
    except RateLimitError as error:
        return make_response({'error': str(error)}, 429)

    profile = merge_profiles(github_profile, bitbucket_profile)
    return make_response(profile, 200)
