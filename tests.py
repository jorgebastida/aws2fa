import os
import sys
import unittest
import tempfile
from datetime import datetime

try:
    from mock import patch, Mock, call
except ImportError:
    from unittest.mock import patch, Mock

from aws2fa import AWS2FA
from aws2fa.bin import main
from aws2fa.helpers import ConfigParser


class TestAWS2FA(unittest.TestCase):

    def assert_config_section(self, path, section, value):
        parser = ConfigParser()
        parser.read(path)
        config = dict(parser.items(section))
        self.assertEqual(config, value)

    def set_config(self, path, conf):
        with open(path, 'w') as f:
            f.write("\n".join(conf))

    def test_help(self):

        try:
            main(['aws2fa', '--help'])
        except SystemExit as e:
            self.assertEqual(e.code, 0)

    @patch('aws2fa.bin.AWS2FA._get_sts_client')
    @patch('aws2fa.bin.AWS2FA._user_input')
    @patch('aws2fa.bin.AWS2FA._get_configuration_path')
    def test_general_no_profile(self, _get_configuration_path, _user_input, _get_sts_client):

        # Set user configuration

        config_path = tempfile.mkdtemp()

        self.set_config(
            os.path.join(config_path, 'credentials'),
            [
                "[default]",
                "aws_secret_access_key = SECRET_ACCESS_KEY",
                "aws_access_key_id = ACCESS_KEY_ID",
            ]
        )

        self.set_config(
            os.path.join(config_path, 'config'),
            [
                "[default]",
                "region = eu-west-1",
            ]
        )

        # Configure mocks

        _get_sts_client.return_value.get_session_token.return_value = {
            'Credentials': {
                'SessionToken': 'TEMP_SESSION_TOKEN',
                'SecretAccessKey': 'TEMP_SECRET_ACCESS_KEY',
                'AccessKeyId': 'TEMP_ACCESS_KEY_ID',
                'Expiration': datetime.now()
            }
        }

        _get_configuration_path.return_value = config_path
        _user_input.side_effect = [
            "device-arn",
            "123456"
        ]

        # Run aws2fa

        out = main(['aws2fa'])

        # Test

        _get_sts_client.return_value.get_session_token.assert_called_once_with(
            DurationSeconds=43200,
            SerialNumber='device-arn',
            TokenCode='123456'
        )

        self.assert_config_section(
            os.path.join(config_path, 'credentials'),
            'default',
            {
                'aws_access_key_id': 'TEMP_ACCESS_KEY_ID',
                'aws_secret_access_key': 'TEMP_SECRET_ACCESS_KEY',
                'aws_session_token': 'TEMP_SESSION_TOKEN'
            }
        )

        self.assert_config_section(
            os.path.join(config_path, 'credentials'),
            'default::source-profile',
            {
                'aws_access_key_id': 'ACCESS_KEY_ID',
                'aws_secret_access_key': 'SECRET_ACCESS_KEY',
            }
        )

        self.assert_config_section(
            os.path.join(config_path, 'config'),
            'default',
            {
                'mfa_serial': 'device-arn',
                'region': 'eu-west-1',
                'source_profile': 'default::source-profile'
            }
        )

        self.assertEqual(out, 0)

    @patch('aws2fa.bin.AWS2FA._get_sts_client')
    @patch('aws2fa.bin.AWS2FA._user_input')
    @patch('aws2fa.bin.AWS2FA._get_configuration_path')
    def test_general_with_profile(self, _get_configuration_path, _user_input, _get_sts_client):

        # Set user configuration

        config_path = tempfile.mkdtemp()

        self.set_config(
            os.path.join(config_path, 'credentials'),
            [
                "[default]",
                "aws_secret_access_key = SECRET_ACCESS_KEY",
                "aws_access_key_id = ACCESS_KEY_ID",
                "",
                "[my-profile]",
                "aws_secret_access_key = PROFILE_SECRET_ACCESS_KEY",
                "aws_access_key_id = PROFILE_ACCESS_KEY_ID",
            ]
        )

        self.set_config(
            os.path.join(config_path, 'config'),
            [
                "[default]",
                "region = eu-west-1",
                "",
                "[profile my-profile]",
                "region = eu-west-2",
            ]
        )

        # Configure mocks

        _get_sts_client.return_value.get_session_token.return_value = {
            'Credentials': {
                'SessionToken': 'TEMP_SESSION_TOKEN',
                'SecretAccessKey': 'TEMP_SECRET_ACCESS_KEY',
                'AccessKeyId': 'TEMP_ACCESS_KEY_ID',
                'Expiration': datetime.now()
            }
        }

        _get_configuration_path.return_value = config_path
        _user_input.side_effect = [
            "device-arn",
            "123456"
        ]

        # Run aws2fa

        out = main(['aws2fa', 'my-profile'])

        # Test

        _get_sts_client.return_value.get_session_token.assert_called_once_with(
            DurationSeconds=43200,
            SerialNumber='device-arn',
            TokenCode='123456'
        )

        self.assert_config_section(
            os.path.join(config_path, 'credentials'),
            'default',
            {
                'aws_access_key_id': 'ACCESS_KEY_ID',
                'aws_secret_access_key': 'SECRET_ACCESS_KEY',
            }
        )

        self.assert_config_section(
            os.path.join(config_path, 'credentials'),
            'my-profile',
            {
                'aws_access_key_id': 'TEMP_ACCESS_KEY_ID',
                'aws_secret_access_key': 'TEMP_SECRET_ACCESS_KEY',
                'aws_session_token': 'TEMP_SESSION_TOKEN'
            }
        )

        self.assert_config_section(
            os.path.join(config_path, 'credentials'),
            'my-profile::source-profile',
            {
                'aws_access_key_id': 'PROFILE_ACCESS_KEY_ID',
                'aws_secret_access_key': 'PROFILE_SECRET_ACCESS_KEY',
            }
        )

        self.assert_config_section(
            os.path.join(config_path, 'config'),
            'default',
            {
                'region': 'eu-west-1'
            }
        )

        self.assert_config_section(
            os.path.join(config_path, 'config'),
            'profile my-profile',
            {
                'mfa_serial': 'device-arn',
                'region': 'eu-west-2',
                'source_profile': 'my-profile::source-profile'
            }
        )

        self.assertEqual(out, 0)
