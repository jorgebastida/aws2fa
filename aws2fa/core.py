import os

import boto3
from botocore.client import ClientError

from .helpers import ConfigParser
from . import exceptions


class AWS2FA(object):

    def __init__(self, **kwargs):
        self._devices_path = os.path.join(self._get_configuration_path(), 'devices')
        self._credentials_path = os.path.join(self._get_configuration_path(), 'credentials')
        self._master_credentials_path = os.path.join(self._get_configuration_path(), 'credentials_master')
        self.profile = kwargs.get('profile')
        self.hours = kwargs.get('hours')
        self._profile_credentials = self._get_profile_credentials()
        self._profile_device = self._get_profile_device()
        self.client = boto3.client(
            'sts',
            aws_access_key_id=self._profile_credentials['aws_access_key_id'],
            aws_secret_access_key=self._profile_credentials['aws_secret_access_key'],
        )

    def _get_configuration_path(self):
        return os.path.join(os.path.expanduser('~'), '.aws')

    def _get_credentials_config(self, path):
        """Returns a ConfigParser instance for the give ``path``"""
        parser = ConfigParser()
        success = parser.read(path)
        return parser

    def _get_profile_credentials(self):
        """Returns a dictionary with aws credentials.
        Configuration in the master credentials path has higher priority than
        the original credentials path.
        If no configuration files are found, ``InvalidProfileError`` will be
        raised.
        """
        for source in (self._master_credentials_path, self._credentials_path):
            parser = self._get_credentials_config(source)
            if parser.has_section(self.profile):
                return dict(parser.items(self.profile))
        raise exceptions.InvalidProfileError()

    def _get_devices(self):
        """Returns a ConfigParser instance for the devices"""
        parser = ConfigParser()
        success = parser.read(self._devices_path)
        if not success:
            return self._setup_profile_device()
        return parser

    def _get_profile_device(self):
        """Returns the device configuration for the current profile.
        If the configuration is not present, ``_setup_profile_device`` will
        be called so it is fulfill"""
        parser = self._get_devices()
        if not parser.has_section(self.profile):
            parser = self._setup_profile_device()
        return dict(parser.items(self.profile))

    def _setup_profile_device(self):
        """Returns a ConfigParser instance for the device configuration after
        asking the user the serial number of the device."""
        parser = ConfigParser()
        parser.read(self._devices_path)
        serial_number = raw_input("2FA device serial number for profile '{}': ".format(self.profile))
        parser.add_section(self.profile)
        parser.set(self.profile, 'serial_number', serial_number)
        with open(self._devices_path, 'wb') as f:
            parser.write(f)
        return parser

    def get_duration(self):
        """Returns the number of seconds for which the token will be valid."""
        return self.hours * 60 * 60

    def get_serial_number(self):
        """Returns the serial_number of the device configured in this profile."""
        return self._profile_device["serial_number"]

    def get_token_code(self):
        """Asks and return the the user 2FA token after some basic validation."""
        token_code = ""
        while len(token_code) != 6:
            token_code = raw_input("2FA code: ")
        return token_code

    def _save_master_credentials_if_required(self):
        """Stores in the master credentials config file both the
        ``aws_secret_access_key`` and ``aws_access_key_id`` present in the
        original ``credentials`` file."""
        profile_credentials = dict(self._get_credentials_config(self._credentials_path).items(self.profile))
        master_parser = self._get_credentials_config(self._master_credentials_path)
        if not master_parser.has_section(self.profile):
            master_parser.add_section(self.profile)
            master_parser.set(self.profile, 'aws_secret_access_key', profile_credentials['aws_secret_access_key'])
            master_parser.set(self.profile, 'aws_access_key_id', profile_credentials['aws_access_key_id'])
            with open(self._master_credentials_path, 'wb') as f:
                master_parser.write(f)

    def _set_session_credentials(self, **kwargs):
        """Stores the credentials in ``kwargs`` in the credentials file."""
        self._save_master_credentials_if_required()
        parser = self._get_credentials_config(self._credentials_path)
        for k, v in kwargs.items():
            parser.set(self.profile, k, v)

        with open(self._credentials_path, 'wb') as f:
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
