import os

import boto3
from botocore.client import ClientError

from .helpers import ConfigParser
from . import exceptions

try:
    input = raw_input
except NameError:
    pass


class AWS2FA(object):

    def __init__(self, **kwargs):
        self._config_path = os.path.join(self._get_configuration_path(), 'config')
        self._credentials_path = os.path.join(self._get_configuration_path(), 'credentials')
        self.profile = kwargs.get('profile')
        self.hours = kwargs.get('hours')
        self._profile_credentials = self._get_profile_credentials()
        self._profile_device = self._get_profile_device()
        self.client = self._get_sts_client()

    def _get_sts_client(self):
        return boto3.client(
            'sts',
            aws_access_key_id=self._profile_credentials['aws_access_key_id'],
            aws_secret_access_key=self._profile_credentials['aws_secret_access_key'],
        )

    def _user_input(self, message):
        return input(message).strip()

    def _get_configuration_path(self):
        return os.path.join(os.path.expanduser('~'), '.aws')

    def _get_credentials_config(self, path):
        """Returns a ConfigParser instance for the give ``path``"""
        parser = ConfigParser()
        parser.read(path)
        return parser

    def _get_source_profile_name(self):
        return u"{}::source-profile".format(self.profile)

    def _get_profile_credentials(self):
        """Returns a dictionary with aws credentials.
        Configuration for a profile named $profile::source-profile has higher
        priority than $profile.
        If no configuration files are found, ``InvalidProfileError`` will be
        raised.
        """
        parser = self._get_credentials_config(self._credentials_path)
        if parser.has_section(self._get_source_profile_name()):
            return dict(parser.items(self._get_source_profile_name()))
        if parser.has_section(self.profile):
            return dict(parser.items(self.profile))
        raise exceptions.InvalidProfileError()

    def _get_config(self):
        """Returns a ConfigParser instance for the config file"""
        parser = ConfigParser()
        parser.read(self._config_path)
        return parser

    def _config_profile_name(self):
        if self.profile == "default":
            return self.profile
        return "profile {}".format(self.profile)

    def _get_profile_device(self):
        """Returns the device for the current profile.
        If the configuration is not present, ``_setup_profile_device`` will
        be called so it is fulfill"""
        parser = self._get_config()
        if parser.has_section(self._config_profile_name()):
            config = dict(parser.items(self._config_profile_name()))
            return config.get('mfa_serial') or self._setup_profile_device()
        return self._setup_profile_device()

    def _setup_profile_device(self):
        """Returns and configure the device for the current profile."""
        parser = self._get_config()
        serial_number = self._user_input("2FA device ARN for profile '{}': ".format(self.profile)).strip()

        if not parser.has_section(self._config_profile_name()):
            parser.add_section(self._config_profile_name())
        parser.set(self._config_profile_name(), 'mfa_serial', serial_number)

        configuration = dict(parser.items(self._config_profile_name()))

        # Add a default region if it is not present
        if 'region' not in configuration:
            default_region = dict(parser.items('default')).get('region', 'us-west-2')
            parser.set(self._config_profile_name(), 'region', default_region)

        # Add source_profile if it is not present
        if 'source_profile' not in configuration:
            parser.set(self._config_profile_name(), 'source_profile', self._get_source_profile_name())

        with open(self._config_path, 'w') as f:
            parser.write(f)
        return serial_number

    def get_duration(self):
        """Returns the number of seconds for which the token will be valid."""
        return self.hours * 60 * 60

    def get_serial_number(self):
        """Returns the serial_number of the device configured in this profile."""
        return self._profile_device

    def get_token_code(self):
        """Asks and return the the user 2FA token after some basic validation."""
        token_code = ""
        while len(token_code) != 6:
            token_code = self._user_input("Enter 2FA code: ").strip()
        return token_code

    def _save_master_credentials_if_required(self):
        """Stores the master credentials in a profile called
        $profile::source-profile"""
        credentials_parser = self._get_credentials_config(self._credentials_path)
        profile_credentials = dict(credentials_parser.items(self.profile))

        if not credentials_parser.has_section(self._get_source_profile_name()):
            credentials_parser.add_section(self._get_source_profile_name())
            credentials_parser.set(self._get_source_profile_name(), 'aws_secret_access_key', profile_credentials['aws_secret_access_key'])
            credentials_parser.set(self._get_source_profile_name(), 'aws_access_key_id', profile_credentials['aws_access_key_id'])
            with open(self._credentials_path, 'w') as f:
                credentials_parser.write(f)

    def _set_session_credentials(self, **kwargs):
        """Stores the credentials in ``kwargs`` in the credentials file."""
        self._save_master_credentials_if_required()
        parser = self._get_credentials_config(self._credentials_path)
        for k, v in kwargs.items():
            parser.set(self.profile, k, v)

        with open(self._credentials_path, 'w') as f:
            parser.write(f)

        return parser

    def _get_profile_session_token(self):
        """Using boto retrieve the temporal credentials for the current profile."""
        try:
            return self.client.get_session_token(
                DurationSeconds=self.get_duration(),
                SerialNumber=self.get_serial_number(),
                TokenCode=self.get_token_code()
            )
        except ClientError as exc:
            code = exc.response['Error']['Code']
            if code in (u'AccessDenied',):
                print("Invalid 2FA code, try again")
                return self._get_profile_session_token()
            raise

    def run(self):
        profile_session_token = self._get_profile_session_token()
        self._set_session_credentials(
            aws_session_token=profile_session_token['Credentials']['SessionToken'],
            aws_secret_access_key=profile_session_token['Credentials']['SecretAccessKey'],
            aws_access_key_id=profile_session_token['Credentials']['AccessKeyId']
        )

        print(
            "Sucesss! Your credentials will expire on: {}".format(
                profile_session_token['Credentials']['Expiration']
            )
        )
