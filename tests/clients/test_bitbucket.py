from contextlib import ExitStack
from unittest import mock, TestCase

import responses

from clients.bitbucket import config, BitBucketClient
from clients.exceptions import ApiResponseError, UnknownProfileError


class BitBucketClientTestCase(TestCase):
    def test_init_reads_base_url_from_config(self):
        with mock.patch.dict(config, {'bitbucket_base_url': 'base_url'}):
            client = BitBucketClient()
        self.assertTrue(hasattr(client, 'base_url'))
        self.assertEqual(client.base_url, 'base_url')

    @responses.activate
    def test_get_resource_returns_parsed_response_on_success(self):
        client = BitBucketClient()
        test_url = 'https://api.bitbucket.org/2.0/teams/mailchimp'
        test_response = {'username': 'mailchimp'}

        responses.add(responses.GET, test_url, json=test_response, status=200)
        self.assertEqual(client._get_resource(test_url), test_response)

    @responses.activate
    def test_get_resource_raises_error_on_failure(self):
        client = BitBucketClient()
        test_url = 'https://api.bitbucket.org/2.0/teams/mailchimp'
        test_response = {'error': 'this is a test error'}

        responses.add(responses.GET, test_url, json=test_response, status=404)
        with self.assertRaises(ApiResponseError) as cm:
            client._get_resource(test_url)

        self.assertEqual(cm.exception.args, (404, test_response))

    @responses.activate
    def test_get_response_size_returns_size_attribute(self):
        client = BitBucketClient()
        test_url = 'https://api.bitbucket.org/2.0/repositories/user/repo_1/issues'
        test_response = {'size': 43}

        responses.add(responses.GET, test_url, json=test_response, status=200)
        self.assertEqual(client._get_response_size(test_url), 43)

    @responses.activate
    def test_get_response_values_yields_all_values(self):
        client = BitBucketClient()
        test_url_1 = 'https://api.bitbucket.org/2.0/repositories/user/repo_1/issues'
        test_url_2 = 'https://api.bitbucket.org/2.0/repositories/user/repo_1/issues?page=2'
        test_response_1 = {'values': [1, 2, 3], 'next': test_url_2}
        test_response_2 = {'values': [4, 5, 6]}

        responses.add(responses.GET, test_url_1, json=test_response_1, status=200)
        responses.add(responses.GET, test_url_2, json=test_response_2, status=200)
        self.assertEqual(
            list(client._get_response_values(test_url_1)),
            [1, 2, 3, 4, 5, 6]
        )

    @responses.activate
    def test_get_profile_raises_error_on_missing_profile(self):
        client = BitBucketClient()
        profile_name = 'not-a-profile'
        responses.add(
            responses.GET,
            '{}/users/{}'.format(client.base_url, profile_name),
            json={'error': 'not found'},
            status=404
        )

        with self.assertRaises(UnknownProfileError) as cm:
            client.get_profile(profile_name, is_team=False)

        self.assertEqual(
            str(cm.exception),
            'No such BitBucket account: not-a-profile'
        )

    @responses.activate
    def test_get_profile_aggregates_data(self):
        client = BitBucketClient()
        profile_name = 'some-team'
        user_response = {'username': 'some-team'}
        responses.add(
            responses.GET,
            '{}/teams/{}'.format(client.base_url, profile_name),
            json=user_response,
            status=200
        )

        with ExitStack() as stack:
            context_managers = (
                mock.patch.object(client, '_get_user_data', return_value={'user': 'data'}),
                mock.patch.object(client, '_get_repository_data', return_value={'repo': 'data'}),
            )
            for context_manager in context_managers:
                stack.enter_context(context_manager)

            data = client.get_profile(profile_name)
            client._get_user_data.assert_called_once_with(user_response)
            client._get_repository_data.assert_called_once_with(user_response)
            self.assertEqual(data, {'user': 'data', 'repo': 'data'})

    def test_get_user_data_retrieves_data(self):
        client = BitBucketClient()
        user = {
            'links': {
                'followers': {'href': 'followers_link'},
                'following': {'href': 'following_link'},
            }
        }

        with mock.patch.object(client, '_get_response_size') as mock_get_size:
            data = client._get_user_data(user)

        mock_get_size.assert_any_call('followers_link')
        mock_get_size.assert_any_call('following_link')
        self.assertEqual(
            data,
            {
                'followers': mock_get_size.return_value,
                'following': mock_get_size.return_value,
            }
        )

    def test_get_repository_data_retrieves_data(self):
        client = BitBucketClient()
        user = {
            'username': 'some_username',
            'links': {'repositories': {'href': 'repositories_link'}}
        }
        repositories = [
            {
                'slug': 'some_repo',
                'has_issues': True,
                'language': 'Erlang',
                'links': {
                    'watchers': {'href': 'watchers_link'},
                    'issues': {'href': 'issues_link'},
                }
            },
            {
                'slug': 'some_repo',
                'has_issues': False,
                'language': '',
                'links': {
                    'watchers': {'href': 'watchers_link'},
                }
            },
        ]

        with ExitStack() as stack:
            context_managers = (
                mock.patch.object(client, '_get_response_values'),
                mock.patch.object(client, '_get_response_size', return_value=3),
            )
            for context_manager in context_managers:
                stack.enter_context(context_manager)

            client._get_response_values.side_effect = (
                repositories,
                ['commit_1', 'commit_2', 'commit_3'],
                []
            )

            data = client._get_repository_data(user)
            self.assertEqual(
                data,
                {
                    'repositories': 2,
                    'watchers': 6,
                    'commits': 3,
                    'issues': 3,
                    'languages': ['Erlang']
                }
            )
