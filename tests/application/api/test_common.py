import json
from unittest import mock, TestCase

from application.api import common


class MakeResponseTestCase(TestCase):
    def test_serializes_content(self):
        with mock.patch.object(common, 'make_flask_response') as mock_make_response:
            response = common.make_response({'foo': 'bar'}, 200)
        mock_make_response.assert_called_once_with(
            json.dumps({'foo': 'bar'}),
            200,
            {'Content-Type': 'application/json'}
        )
        self.assertEqual(response, mock_make_response.return_value)
