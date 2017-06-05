class BaseAWS2FAException(Exception):

    code = 1

    def hint(self):
        return "Unknown Error."


class InvalidProfileError(BaseAWS2FAException):

    code = 2

    def hint(self):
        return "The provided profile name is not present in your ~/.aws/credentials file"


class CredentialsNotFoundError(BaseAWS2FAException):

    code = 3

    def hint(self):
        return "Credentials file ~/.aws/credentials not found"
