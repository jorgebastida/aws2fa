import sys
import argparse

import boto3
from botocore.client import ClientError

from . import exceptions
from .core import AWS2FA
from ._version import __version__


def main(argv=None):

    argv = (argv or sys.argv)[1:]

    parser = argparse.ArgumentParser(usage=("%(prog)s [profile]"))
    parser.add_argument("--version", action="version",
                        version="%(prog)s " + __version__)

    parser.add_argument("profile",
                        type=str,
                        default="default",
                        nargs='?',
                        help="aws-cli profile name")

    parser.add_argument("--hours",
                        type=int,
                        default=12,
                        help="number of hours for which the token will be valid")

    # Parse input
    options, args = parser.parse_known_args(argv)
    try:
        aws2fa = AWS2FA(**vars(options))
        aws2fa.run()
    except ClientError as exc:
        code = exc.response['Error']['Code']
        if code in (u'AccessDeniedException', u'SignatureDoesNotMatch', u'InvalidClientTokenId'):
            hint = exc.response['Error'].get('Message', 'AccessDeniedException')
            sys.stderr.write("Your credentials look invalid. Error: {}\n".format(hint))
            return 4
        raise
    except exceptions.BaseAWS2FAException as exc:
        sys.stderr.write("{0}\n".format(exc.hint()))
        return exc.code
    except Exception:
        import platform
        import traceback
        options = vars(options)
        options['aws_access_key_id'] = 'SENSITIVE'
        options['aws_secret_access_key'] = 'SENSITIVE'
        options['aws_session_token'] = 'SENSITIVE'
        options['aws_profile'] = 'SENSITIVE'
        sys.stderr.write("\n")
        sys.stderr.write("=" * 80)
        sys.stderr.write("\nYou've found a bug! Please, raise an issue attaching the following traceback\n")
        sys.stderr.write("https://github.com/jorgebastida/aws2fa/issues/new\n")
        sys.stderr.write("-" * 80)
        sys.stderr.write("\n")
        sys.stderr.write("Version: {0}\n".format(__version__))
        sys.stderr.write("Python: {0}\n".format(sys.version))
        sys.stderr.write("boto3 version: {0}\n".format(boto3.__version__))
        sys.stderr.write("Platform: {0}\n".format(platform.platform()))
        sys.stderr.write("Config: {0}\n".format(options))
        sys.stderr.write("Args: {0}\n\n".format(sys.argv))
        sys.stderr.write(traceback.format_exc())
        sys.stderr.write("=" * 80)
        sys.stderr.write("\n")
        return 1

    return 0
