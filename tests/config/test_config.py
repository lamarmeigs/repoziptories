import os
from unittest import mock, TestCase

import yaml

import config


class GetConfigTestCase(TestCase):
    def _backup_config(self):
        if os.path.isfile('config/config.yaml'):
            os.rename('config/config.yaml', 'config/config.yaml.testing-backup')

    def _write_config(self, testing_config):
        with open('config/config.yaml', 'w') as config_file:
            config_file.write(yaml.dump(testing_config))

    def _restore_backups(self):
        if os.path.isfile('config/config.yaml.testing-backup'):
            os.rename('config/config.yaml.testing-backup', 'config/config.yaml')

    def setUp(self):
        super().setUp()
        self._backup_config()

    def tearDown(self):
        os.unlink('config/config.yaml')
        self._restore_backups()
        return super().tearDown()

    def test_load_yaml_file(self):
        config_to_write = {'some_config_key': 'some_config_val'}
        self._write_config(config_to_write)
        loaded_config = config._get_config('config/config.yaml')
        self.assertEqual(loaded_config, config_to_write)

    def test_override_yaml_from_envvar(self):
        self._write_config({'some_config_key': 'some_config_val'})
        with mock.patch.dict(os.environ, {'some_config_key': 'other_val'}):
            loaded_config = config._get_config('config/config.yaml')
        self.assertEqual(loaded_config, {'some_config_key': 'other_val'})


class LoadedConfigTestCase(TestCase):
    def test_config_attr_exists(self):
        self.assertTrue(hasattr(config, 'config'))
        self.assertIsInstance(config.config, dict)
