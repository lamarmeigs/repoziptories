import json
from unittest import mock, TestCase

from application import helpers


class MakeResponseTestCase(TestCase):
    def test_serializes_content(self):
        with mock.patch.object(helpers, 'make_flask_response') as mock_make_response:
            response = helpers.make_response({'foo': 'bar'}, 200)
        mock_make_response.assert_called_once_with(
            json.dumps({'foo': 'bar'}),
            200,
            {'Content-Type': 'application/json'}
        )
        self.assertEqual(response, mock_make_response.return_value)


class MergeProfilesTestCase(TestCase):
    def test_merges_profiles(self):
        profile_1 = {
            'repositories': {'original': 1, 'forked': 2},
            'stars': 3,
            'starred': 9,
            'issues': 4,
            'followers': 5,
            'following': 6,
            'commits': 7,
            'languages': ['Fortran'],
            'topics': ['web applications'],
        }
        profile_2 = {'repositories': 8, 'languages': ['Fortran']}
        profile_3 = None

        merged_profile = helpers.merge_profiles(profile_1, profile_2, profile_3)
        self.assertEqual(
            merged_profile,
            {
                'repositories': {'original': 9, 'forked': 2},
                'stars': 3,
                'starred': 9,
                'issues': 4,
                'followers': 5,
                'following': 6,
                'commits': 7,
                'languages': ['Fortran'],
                'topics': ['web applications'],
            }
        )
