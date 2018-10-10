from contextlib import ExitStack
from unittest import mock, TestCase

from application.api.v1 import endpoints
from clients import exceptions


class GetMergedProfilesTestCase(TestCase):
    def test_retrieves_profiles(self):
        with ExitStack() as stack:
            context_managers = (
                mock.patch.object(endpoints.GithubClient, 'get_profile'),
                mock.patch.object(endpoints.BitBucketClient, 'get_profile'),
                mock.patch.object(endpoints, 'make_response'),
            )
            for context_manager in context_managers:
                stack.enter_context(context_manager)

            with endpoints.app.test_request_context('/v1/profile/username?github_username=gh_user'):
                response = endpoints.get_merged_profiles_v1('username')

            endpoints.GithubClient.get_profile.assert_called_once_with('gh_user')
            endpoints.BitBucketClient.get_profile.assert_called_once_with('username', is_team=True)
            endpoints.make_response.assert_called_once_with(
                {
                    'github': endpoints.GithubClient.get_profile.return_value,
                    'bitbucket': endpoints.BitBucketClient.get_profile.return_value,
                },
                200
            )
            self.assertEqual(response, endpoints.make_response.return_value)

    def test_ignores_missing_github_profile(self):
        error = exceptions.UnknownProfileError()
        with ExitStack() as stack:
            context_managers = (
                mock.patch.object(endpoints.GithubClient, 'get_profile', side_effect=error),
                mock.patch.object(endpoints.BitBucketClient, 'get_profile'),
                mock.patch.object(endpoints, 'make_response'),
            )
            for context_manager in context_managers:
                stack.enter_context(context_manager)

            with endpoints.app.test_request_context('/v1/profile/username'):
                response = endpoints.get_merged_profiles_v1('username')

            endpoints.GithubClient.get_profile.assert_called_once_with('username')
            endpoints.BitBucketClient.get_profile.assert_called_once_with('username', is_team=True)
            endpoints.make_response.assert_called_once_with(
                {
                    'github': None,
                    'bitbucket': endpoints.BitBucketClient.get_profile.return_value,
                },
                200
            )
            self.assertEqual(response, endpoints.make_response.return_value)

    def test_raises_error_on_github_rate_limit(self):
        error = exceptions.RateLimitError('this is a test')
        with ExitStack() as stack:
            context_managers = (
                mock.patch.object(endpoints.GithubClient, 'get_profile', side_effect=error),
                mock.patch.object(endpoints.BitBucketClient, 'get_profile'),
                mock.patch.object(endpoints, 'make_response'),
            )
            for context_manager in context_managers:
                stack.enter_context(context_manager)

            with endpoints.app.test_request_context('/v1/profile/username'):
                response = endpoints.get_merged_profiles_v1('username')

            endpoints.make_response.assert_called_once_with(
                {'error': 'this is a test'},
                429
            )
            self.assertEqual(response, endpoints.make_response.return_value)

    def test_raises_error_on_invalid_github_credentials(self):
        error = exceptions.InvalidCredentialsError('this is a test')
        with ExitStack() as stack:
            context_managers = (
                mock.patch.object(endpoints.GithubClient, 'get_profile', side_effect=error),
                mock.patch.object(endpoints.BitBucketClient, 'get_profile'),
                mock.patch.object(endpoints, 'make_response'),
            )
            for context_manager in context_managers:
                stack.enter_context(context_manager)

            with endpoints.app.test_request_context('/v1/profile/username'):
                response = endpoints.get_merged_profiles_v1('username')

            endpoints.make_response.assert_called_once_with(
                {'error': 'this is a test'},
                401
            )
            self.assertEqual(response, endpoints.make_response.return_value)

    def test_ignores_missing_bitbucket_profile(self):
        error = exceptions.UnknownProfileError()
        with ExitStack() as stack:
            context_managers = (
                mock.patch.object(endpoints.GithubClient, 'get_profile'),
                mock.patch.object(endpoints.BitBucketClient, 'get_profile', side_effect=error),
                mock.patch.object(endpoints, 'make_response'),
            )
            for context_manager in context_managers:
                stack.enter_context(context_manager)

            with endpoints.app.test_request_context('/v1/profile/username'):
                response = endpoints.get_merged_profiles_v1('username')

            endpoints.GithubClient.get_profile.assert_called_once_with('username')
            endpoints.BitBucketClient.get_profile.assert_called_once_with('username', is_team=True)
            endpoints.make_response.assert_called_once_with(
                {
                    'github': endpoints.GithubClient.get_profile.return_value,
                    'bitbucket': None,
                },
                200
            )
            self.assertEqual(response, endpoints.make_response.return_value)

    def test_raises_error_on_bitbucket_rate_limit(self):
        error = exceptions.RateLimitError('this is a test')
        with ExitStack() as stack:
            context_managers = (
                mock.patch.object(endpoints.GithubClient, 'get_profile'),
                mock.patch.object(endpoints.BitBucketClient, 'get_profile', side_effect=error),
                mock.patch.object(endpoints, 'make_response'),
            )
            for context_manager in context_managers:
                stack.enter_context(context_manager)

            with endpoints.app.test_request_context('/v1/profile/username'):
                response = endpoints.get_merged_profiles_v1('username')

            endpoints.make_response.assert_called_once_with(
                {'error': 'this is a test'},
                429
            )
            self.assertEqual(response, endpoints.make_response.return_value)
