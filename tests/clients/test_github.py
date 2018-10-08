from contextlib import ExitStack
from unittest import mock, TestCase

import github

from clients.exceptions import UnknownProfileError
from clients.github import GithubClient


class GithubClientTestCase(TestCase):
    def test_init_creates_client(self):
        client = GithubClient()
        self.assertTrue(hasattr(client, 'client'))
        self.assertIsInstance(client.client, github.Github)

    def test_get_profile_raises_error_on_unknown_user(self):
        client = GithubClient()
        error = github.UnknownObjectException('test error', None)
        with mock.patch.object(client.client, 'get_user', side_effect=error):
            with self.assertRaises(UnknownProfileError) as cm:
                client.get_profile('foobar')

        self.assertEqual(str(cm.exception), 'No such GitHub account: foobar')

    def test_get_profile_assembles_profile_data(self):
        client = GithubClient()
        with ExitStack() as stack:
            context_managers = (
                mock.patch.object(client.client, 'get_user'),
                mock.patch.object(client, '_get_user_data', return_value={'user': 'data'}),
                mock.patch.object(client, '_get_repository_data', return_value={'repo': 'data'}),
                mock.patch.object(client, '_get_misc_data', return_value={'misc': 'data'}),
            )
            for context_manager in context_managers:
                stack.enter_context(context_manager)

            data = client.get_profile('foobar')
            client._get_user_data.assert_called_once_with(
                client.client.get_user.return_value
            )
            client._get_repository_data.assert_called_once_with(
                client.client.get_user.return_value
            )
            client._get_misc_data.assert_called_once_with(
                client.client.get_user.return_value
            )
            self.assertEqual(
                data,
                {'user': 'data', 'repo': 'data', 'misc': 'data'}
            )

    def test_get_user_data_retrieves_data(self):
        user = mock.MagicMock()
        user.followers = 5
        user.following = 2
        user.get_starred.return_value.totalCount = 8

        data = GithubClient._get_user_data(user)
        self.assertEqual(data, {'followers': 5, 'following': 2, 'starred': 8})

    def test_get_repository_data_retrieves_data(self):
        user = mock.MagicMock()
        user.get_repos.return_value = [
            mock.MagicMock(
                forked=True,
                stargazers_count=2,
                language='Python',
                topics=['test', 'repositories']
            ),
            mock.MagicMock(
                forked=False,
                stargazers_count=3,
                language='JavaScript',
                topics=None,
            )
        ]

        data = GithubClient._get_repository_data(user)
        self.assertIsInstance(data, dict)
        self.assertEqual(data['repositories'], {'original': 1, 'forked': 1})
        self.assertEqual(data['stars'], 5)
        self.assertCountEqual(data['languages'], ['Python', 'JavaScript'])
        self.assertCountEqual(data['topics'], ['test', 'repositories'])

    def test_get_misc_data_retrieves_data(self):
        client = GithubClient()
        user = mock.MagicMock(login='foobar')
        with mock.patch.object(client.client, 'search_issues') as mock_search:
            mock_search.return_value.totalCount = 4
            data = client._get_misc_data(user)

        mock_search.assert_called_once_with('author:foobar')
        self.assertEqual(data, {'issues': 4})
