import requests

from clients.exceptions import ApiResponseError, RateLimitError, UnknownProfileError
from config import config


class BitBucketClient:
    """Provides a basic interface for retrieving relevant data from BitBucket"""

    def __init__(self):
        self.base_url = config['bitbucket_base_url']

    @staticmethod
    def _get_resource(url):
        response = requests.get(url)
        if 200 <= response.status_code <= 299:
            return response.json()
        elif response.status_code == 429:
            raise RateLimitError('Exceeded BitBucket rate limit')
        else:
            raise ApiResponseError(response.status_code, response.json())

    def _get_response_size(self, url):
        response = self._get_resource(url)
        return response.get('size')

    def _get_response_values(self, url):
        next_page = url
        while next_page:
            response = self._get_resource(next_page)
            next_page = response.get('next')
            for value in response['values']:
                yield value

    def get_profile(self, profile_name, is_team=True):
        """Retrieve all relevant data from the named profile.

        Args:
            profile_name (str): name of the BitBucket user whose public data to
                retrieve
            is_team (bool): indicates whether the specified profile is for a
                team (the default) or an individual user

        Return:
            a dict of retrieved API data
        """
        response = requests.get(
            '{}/{}/{}'.format(
                self.base_url,
                'teams' if is_team else 'users',
                profile_name
            )
        )
        if response.status_code == 404:
            raise UnknownProfileError(
                'No such BitBucket account: {}'.format(profile_name)
            )
        user = response.json()

        profile_data = {}
        profile_data.update(self._get_user_data(user))
        profile_data.update(self._get_repository_data(user))
        return profile_data

    def _get_user_data(self, user):
        """Retrieve data related to the given user account.

        Args:
            user (dict): a parsed response from the /user API

        Return:
            a dict containing:
                - the number of followers
                - the number of other users followed
        """
        followers_endpoint = user['links']['followers']['href']
        following_endpoint = user['links']['following']['href']
        return {
            'followers': self._get_response_size(followers_endpoint),
            'following': self._get_response_size(following_endpoint),
        }

    def _get_repository_data(self, user):
        """Retrieve data related to the given user's repositories.

        Args:
            user (dict): a parsed response from the /user API

        Return:
            a dict containing:
                - the number of repositories
                - the total number of commits in their repositories
                - the total number of issues on their repositories
                - the total number of watchers
                - a list of languages used
        """
        repositories = 0
        watchers = 0
        commits = 0
        issues = 0
        languages = set()

        repo_endpoint = user['links']['repositories']['href']
        for repo in self._get_response_values(repo_endpoint):
            repositories += 1

            watcher_endpoint = repo['links']['watchers']['href']
            watchers += self._get_response_size(watcher_endpoint)

            commits_endpoint = '{}/repositories/{}/{}/commits'.format(
                self.base_url,
                user['username'],
                repo['slug'],
            )
            commits += len(list(self._get_response_values(commits_endpoint)))

            if repo['has_issues']:
                issues_endpoint = repo['links']['issues']['href']
                issues += self._get_response_size(issues_endpoint)

            if repo['language']:
                languages.add(repo['language'])

        return {
            'repositories': repositories,
            'watchers': watchers,
            'commits': commits,
            'issues': issues,
            'languages': list(languages),
        }
