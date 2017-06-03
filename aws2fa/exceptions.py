class BaseAWS2FAException(Exception):

    code = 1

    def hint(self):
        return "Unknown Error."


class InvalidProfileError(BaseAWS2FAException):

    code = 2
    hint = "The provided profile name is not present in your ~/.aws/credentials file"


class CredentialsNotFoundError(BaseAWS2FAException):

    code = 2
    hint = "Credentials file ~/.aws/credentials not found"
