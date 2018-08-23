from collections import OrderedDict
import sys
import unittest

import mock

sys.path.append('../')
from bluecat import Gateway  # noqa


class TestBluecat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api_json = {
            'resources': {
                'resource_name': {
                    'get': {
                        'query_parameters': {
                            "PARAM1": {
                                'name': 'PARAM1',
                                'in': 'body',
                                'required': 'true',
                                'type': 'string',
                            },
                            'PARAM2': {
                              'name': 'PARAM2',
                              'in': 'body',
                              'required': 'true',
                              'type': 'integer',
                            },
                            'PARAM3': {
                              'name': 'PARAM3',
                              'in': 'body',
                              'required': 'false',
                              'type': 'boolean',
                            },
                        },
                        'paths': [
                            '/RESOURCE_NAME1/{path_param1}/',
                            '/RESOURCE_NAME1/{configuration}/RESOURCE_NAME2/{view}/',
                            '/RESOURCE_NAME2/{path_param2}/RESOURCE_NAME1/{path_param1}/',
                            '/RESOURCE_NAME1/{path_param1}/RESOURCE_NAME3/{path_param3}/RESOURCE_NAME2/{path_param2}/',
                            '/RESOURCE_NAME1/{path_param1}/RESOURCE_NAME2/{path_param2}/RESOURCE_NAME2',
                        ],
                        'path_parameters': {
                            '/RESOURCE_NAME1/{path_param1}/': {
                                'path_param1': {
                                    'in': 'path',
                                    'name': 'path_param1',
                                    'required': 'true',
                                    'type': 'string',
                                }
                            },
                            '/RESOURCE_NAME1/{path_param1}/RESOURCE_NAME2/{path_param2}/': {
                                'path_param1': {
                                    'in': 'path',
                                    'name': 'path_param1',
                                    'required': 'true',
                                    'type': 'string',
                                },
                                'path_param2': {
                                    'in': 'path',
                                    'name': 'path_param2',
                                    'type': 'string',
                                    'required': 'true',
                                },
                            },
                            '/RESOURCE_NAME2/{path_param2}/RESOURCE_NAME1/{path_param1}/': {
                                'path_param1': {
                                    'in': 'path',
                                    'name': 'path_param1',
                                    'required': 'true',
                                    'type': 'string',
                                },
                                'path_param2': {
                                    'in': 'path',
                                    'name': 'path_param2',
                                    'type': 'string',
                                    'required': 'true',
                                },
                            },
                            '/RESOURCE_NAME1/{path_param1}/RESOURCE_NAME2/{path_param2}/RESOURCE_NAME2': {
                                'path_param1': {
                                    'in': 'path',
                                    'name': 'path_param1',
                                    'required': 'true',
                                    'type': 'string',
                                },
                                'path_param2': {
                                    'in': 'path',
                                    'name': 'path_param2',
                                    'type': 'string',
                                    'required': 'true',
                                },
                            },
                            '/RESOURCE_NAME1/{path_param1}/RESOURCE_NAME3/{path_param3}/RESOURCE_NAME2/{path_param2}/':
                            {
                                'path_param1': {
                                    'in': 'path',
                                    'name': 'path_param1',
                                    'required': 'true',
                                    'type': 'string',
                                },
                                'path_param2': {
                                    'in': 'path',
                                    'name': 'path_param2',
                                    'type': 'string',
                                    'required': 'true',
                                },
                                'path_param3': {
                                    'in': 'path',
                                    'name': 'path_param2',
                                    'type': 'string',
                                    'required': 'true',
                                },
                            },
                        },
                    },
                },
            },
        }

        cls.protocol = 'http'
        cls.domain = 'test_server'
        cls.version = 1

        cls.username = 'test_username'
        cls.password = 'test_password'

        cls.resource_path = [{'path_param1': 'resource_path1'}, {'path_param2': 'resource_path2'}]
        cls.json_data = {'PARAM1': 'TEST_STRING', 'PARAM2': '100', 'PARAM3': 'true'}
        cls.kwargs = {'resource_path': cls.resource_path, 'json_data': cls.json_data}

        cls.object = Gateway(
            api_json=cls.api_json['resources'],
            protocol=cls.protocol,
            domain=cls.domain,
            version=cls.version,
            username=cls.username,
            password=cls.password,
            mocked=True,
            **cls.kwargs,
        )

        cls.object.session.post = mock.MagicMock()
        cls.object.session.get = mock.MagicMock()
        cls.object.session.request = mock.MagicMock()

    @classmethod
    def tearDownClass(cls):
        del cls.object

    @mock.patch('bluecat.requests.get')
    @mock.patch('bluecat.requests.Response')
    def test_get_api_json(self, mocked_response, mocked_get):
        mocked_response.json = mock.Mock(return_value=self.api_json)
        mocked_get.return_value = mocked_response

        with mock.patch('builtins.open', new_callable=mock.mock_open()) as m:
            self.object.get_api_json()

            m.assert_called_with('gateway_api.json', 'w')

        mocked_get.assert_called_with(
            '{}://{}/api/v{}/gateway_api_json/'.format(self.protocol, self.domain, self.version)
        )

    def test_login(self):
        self.object.login(self.username, self.password)

        self.object.session.post.assert_called_with(
            '{}://{}/rest_login'.format(self.protocol, self.domain),
            data={'username': 'test_username', 'password': 'test_password'},
        )

    def test_logout(self):
        self.object.logout()

        self.object.session.get.assert_called_with('http://test_server/logout')

    @mock.patch('bluecat.Gateway.login')
    @mock.patch('bluecat.Gateway.logout')
    def test_invoke(self, mocked_login, mocked_logout):
        mocked_login.return_value = None
        mocked_logout.return_value = None

        self.object.invoke('resource_name', 'GET')
        self.object.session.request.assert_called_with(
            'get',
            'http://test_server/api/v1/RESOURCE_NAME1/resource_path1/RESOURCE_NAME2/resource_path2/',
            json={'PARAM1': 'TEST_STRING', 'PARAM2': 100, 'PARAM3': True},
        )

    def test_generate_mocked_response(self):
        response = self.object.generate_mocked_response('RESOURCE_NAME1', 'POST')

        expected_result = 201

        self.assertEqual(response.status_code, expected_result)

        with self.assertRaises(KeyError):
            self.object.generate_mocked_response('RESOURCE_NAME1', 'INVALID_VERB')

    def test_parse_query_params(self):
        definition = self.api_json['resources']['resource_name']['get']
        response = self.object.parse_query_params(definition)

        expected_result = {
            'PARAM1': 'TEST_STRING',
            'PARAM2': 100,
            'PARAM3': True,
        }

        self.assertDictEqual(response, expected_result)

    def test_parse_path_params(self):
        definition = self.api_json['resources']['resource_name']['get']

        response = self.object.parse_path_params(definition, resources=OrderedDict({'path_param1': 'test_path_param1'}))
        paths = [path for path in response.keys()]

        expected_result = '/RESOURCE_NAME1/{path_param1}/'

        self.assertEqual(len(paths), 1)
        self.assertEqual(paths[0], expected_result)

        resources = OrderedDict()
        for resource in self.object.resource_path:
            for key, value in resource.items():
                resources[key] = value
        response = self.object.parse_path_params(definition, resources=resources)
        paths = [path for path in response.keys()]

        expected_result = [
            '/RESOURCE_NAME1/{path_param1}/RESOURCE_NAME2/{path_param2}/',
            '/RESOURCE_NAME1/{path_param1}/RESOURCE_NAME2/{path_param2}/RESOURCE_NAME2',
        ]

        self.assertEqual(len(paths), 2)
        self.assertCountEqual(paths, expected_result)

        definition = self.api_json['resources']['resource_name']['get']
        response = self.object.parse_path_params(definition, resources=OrderedDict({'path_param3': 'test_path_param3'}))
        paths = [path for path in response.keys()]

        self.assertEqual(len(paths), 0)


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBluecat)
    return suite


if __name__ == '__main__':
    unittest.main()
