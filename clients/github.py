import github

from clients.exceptions import RateLimitError, UnknownProfileError


class GithubClient:
    """Provides a basic interface for retrieving relevant data from GitHub"""

    def __init__(self, *args, **kwargs):
        self.client = github.Github(*args, **kwargs)

    def get_profile(self, profile_name):
        """Retrieve all relevant data from the named profile.

        Args:
            profile_name (str): name of the GitHub user whose public data to
                retrieve (eg. kennethreitz)

        Return:
            a dict of retrieved API data

        Raise:
            UnknownProfileError: if the given profile_name does not correspond
                to GitHub user account
            RateLimitError: if the number of requests exceeds GitHub's rate limit
        """
        try:
            user = self.client.get_user(profile_name)
        except github.UnknownObjectException:
            raise UnknownProfileError(
                'No such GitHub account: {}'.format(profile_name)
            )
        except github.RateLimitExceededException:
            raise RateLimitError('Exceeded GitHub rate limit')

        profile = {}
        try:
            profile.update(self._get_user_data(user))
            profile.update(self._get_repository_data(user))
            profile.update(self._get_misc_data(user))
        except github.RateLimitExceededException:
            raise RateLimitError('Exceeded GitHub rate limit')

        return profile

    @staticmethod
    def _get_user_data(user):
        """Retrieve data related to the given user account

        Args:
            user (github.NamedUser.NamedUser): an instantiated GitHub user

        Return:
            a dict containing:
                - the number of followers
                - the number of other users followed
                - the number of stars given
        """
        user_data = {
            'followers': user.followers,
            'following': user.following,
            'starred': user.get_starred().totalCount,
        }
        return user_data

    @staticmethod
    def _get_repository_data(user):
        """Retrieve data related to the given user's repositories.

        Args:
            user (github.NamedUser.NamedUser): an instantiated GitHub user

        Return:
            a dict containing:
                - the number of original repositories
                - the number of forked repositories
                - the total number of stars received on all repositories
                - a list of languages used
                - a list of topics used
                - the total number of commits on original repositories
        """
        original_repo_count = 0
        forked_repo_count = 0
        original_repo_commits = 0
        stars_received = 0
        languages = set()
        topics = set()
        for repo in user.get_repos():
            if not repo.forked:
                original_repo_count += 1
                original_repo_commits += repo.get_commits(author=user).totalCount
            else:
                forked_repo_count += 1
            stars_received += repo.stargazers_count
            if repo.language:
                languages.add(repo.language)
            if repo.topics:
                topics = topics.union(set(repo.topics))

        return {
            'repositories': {
                'original': original_repo_count,
                'forked': forked_repo_count,
            },
            'stars': stars_received,
            'languages': list(languages),
            'topics': list(topics),
        }

    def _get_misc_data(self, user):
        """Retrieve relevant non-user, non-repository profile data.

        Args:
            user (github.NamedUser.NamedUser): an instantiated GitHub user

        Return:
            a dict containing:
                - the number of issues created by the user
        """
        # TODO: Calculate the "size" of the user account
        return {
            'issues': self.client.search_issues('author:{}'.format(user.login)).totalCount
        }
