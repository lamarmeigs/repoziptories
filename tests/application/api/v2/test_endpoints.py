from contextlib import ExitStack
from unittest import mock, TestCase

from application.api.v2 import endpoints
from application.app import app
from clients import exceptions


class GetMergedProfilesTestCase(TestCase):
    def test_retrieves_profiles(self):
        with ExitStack() as stack:
            context_managers = (
                mock.patch.object(endpoints.GithubClient, 'get_profile'),
                mock.patch.object(endpoints.BitBucketClient, 'get_profile'),
                mock.patch.object(endpoints, 'merge_profiles'),
                mock.patch.object(endpoints, 'make_response'),
            )
            for context_manager in context_managers:
                stack.enter_context(context_manager)

            with app.test_request_context('/v2/profile/username?github_username=gh_user'):
                response = endpoints.get_merged_profiles_v2('username')

            endpoints.GithubClient.get_profile.assert_called_once_with('gh_user')
            endpoints.BitBucketClient.get_profile.assert_called_once_with('username', is_team=True)
            endpoints.merge_profiles.assert_called_once_with(
                endpoints.GithubClient.get_profile.return_value,
                endpoints.BitBucketClient.get_profile.return_value,
            )
            endpoints.make_response.assert_called_once_with(
                endpoints.merge_profiles.return_value,
                200
            )
            self.assertEqual(response, endpoints.make_response.return_value)

    def test_ignores_missing_github_profile(self):
        error = exceptions.UnknownProfileError()
        with ExitStack() as stack:
            context_managers = (
                mock.patch.object(endpoints.GithubClient, 'get_profile', side_effect=error),
                mock.patch.object(endpoints.BitBucketClient, 'get_profile'),
                mock.patch.object(endpoints, 'merge_profiles'),
                mock.patch.object(endpoints, 'make_response'),
            )
            for context_manager in context_managers:
                stack.enter_context(context_manager)

            with app.test_request_context('/v2/profile/username'):
                response = endpoints.get_merged_profiles_v2('username')

            endpoints.GithubClient.get_profile.assert_called_once_with('username')
            endpoints.BitBucketClient.get_profile.assert_called_once_with('username', is_team=True)
            endpoints.merge_profiles.assert_called_once_with(
                None,
                endpoints.BitBucketClient.get_profile.return_value,
            )
            endpoints.make_response.assert_called_once_with(
                endpoints.merge_profiles.return_value,
                200
            )
            self.assertEqual(response, endpoints.make_response.return_value)

    def test_raises_error_on_github_rate_limit(self):
        error = exceptions.RateLimitError('this is a test')
        with ExitStack() as stack:
            context_managers = (
                mock.patch.object(endpoints.GithubClient, 'get_profile', side_effect=error),
                mock.patch.object(endpoints.BitBucketClient, 'get_profile'),
                mock.patch.object(endpoints, 'merge_profiles'),
                mock.patch.object(endpoints, 'make_response'),
            )
            for context_manager in context_managers:
                stack.enter_context(context_manager)

            with app.test_request_context('/v2/profile/username'):
                response = endpoints.get_merged_profiles_v2('username')

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
                mock.patch.object(endpoints, 'merge_profiles'),
                mock.patch.object(endpoints, 'make_response'),
            )
            for context_manager in context_managers:
                stack.enter_context(context_manager)

            with app.test_request_context('/v2/profile/username'):
                response = endpoints.get_merged_profiles_v2('username')

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
                mock.patch.object(endpoints, 'merge_profiles'),
                mock.patch.object(endpoints, 'make_response'),
            )
            for context_manager in context_managers:
                stack.enter_context(context_manager)

            with app.test_request_context('/v2/profile/username'):
                response = endpoints.get_merged_profiles_v2('username')

            endpoints.GithubClient.get_profile.assert_called_once_with('username')
            endpoints.BitBucketClient.get_profile.assert_called_once_with('username', is_team=True)
            endpoints.merge_profiles.assert_called_once_with(
                endpoints.GithubClient.get_profile.return_value,
                None
            )
            endpoints.make_response.assert_called_once_with(
                endpoints.merge_profiles.return_value,
                200
            )
            self.assertEqual(response, endpoints.make_response.return_value)

    def test_raises_error_on_bitbucket_rate_limit(self):
        error = exceptions.RateLimitError('this is a test')
        with ExitStack() as stack:
            context_managers = (
                mock.patch.object(endpoints.GithubClient, 'get_profile'),
                mock.patch.object(endpoints.BitBucketClient, 'get_profile', side_effect=error),
                mock.patch.object(endpoints, 'merge_profiles'),
                mock.patch.object(endpoints, 'make_response'),
            )
            for context_manager in context_managers:
                stack.enter_context(context_manager)

            with app.test_request_context('/v2/profile/username'):
                response = endpoints.get_merged_profiles_v2('username')

            endpoints.make_response.assert_called_once_with(
                {'error': 'this is a test'},
                429
            )
            self.assertEqual(response, endpoints.make_response.return_value)
