import os

import boto3
from botocore.client import ClientError

from .helpers import ConfigParser
from . import exceptions


class AWS2FA(object):

    def __init__(self, **kwargs):
        self._devices_path = os.path.join(os.path.expanduser('~'), '.aws', 'devices')
        self._credentials_path = os.path.join(os.path.expanduser('~'), '.aws', 'credentials')
        self.profile = kwargs.get('profile')
        self.hours = kwargs.get('hours')
        self._profile_credentials = self._get_profile_credentials()
        self._profile_device = self._get_profile_device()
        self.client = boto3.client(
            'sts',
            aws_access_key_id=self._profile_credentials['aws_access_key_id'],
            aws_secret_access_key=self._profile_credentials['aws_secret_access_key'],
        )

    def _get_credentials(self):
        parser = ConfigParser()
        success = parser.read(self._credentials_path)
        if not success:
            raise exceptions.CredentialsNotFoundError()
        return parser

    def _get_profile_credentials(self):
        parser = self._get_credentials()
        if parser.has_section(self.profile):
            return dict(parser.items(self.profile))
        else:
            raise exceptions.InvalidProfileError()

    def _get_devices(self):
        parser = ConfigParser()
        success = parser.read(self._devices_path)
        if not success:
            return self._setup_profile_device()
        return parser

    def _get_profile_device(self):
        parser = self._get_devices()
        if not parser.has_section(self.profile):
            parser = self._setup_profile_device()
        return dict(parser.items(self.profile))

    def _setup_profile_device(self):
        parser = ConfigParser()
        parser.read(self._devices_path)
        serial_number = raw_input("2FA Device serial number for profile '{}': ".format(self.profile))
        parser.add_section(self.profile)
        parser.set(self.profile, 'serial_number', serial_number)
        with open(self._devices_path, 'w') as f:
            parser.write(f)
        return parser

    def get_duration(self):
        return self.hours * 60 * 60

    def get_serial_number(self):
        return self._profile_device["serial_number"]

    def get_token_code(self):
        token_code = ""
        while len(token_code) != 6:
            token_code = raw_input("2FA code: ")
        return token_code

    def _set_profile_session_token(self, session_token):
        parser = self._get_credentials()
        parser.set(self.profile, 'aws_session_token', session_token)
        with open(self._credentials_path, 'w') as f:
            parser.write(f)
        return parser

    def _get_profile_session_token(self):
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
        self._set_profile_session_token(
            profile_session_token['Credentials']['SessionToken']
        )

        print(
            "Sucesss! Your token will expire on: {}".format(
                profile_session_token['Credentials']['Expiration']
            )
        )
