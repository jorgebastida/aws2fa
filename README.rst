aws2fa
=======

``aws2fa`` is a simple command to handle 2fa authentication respecting ``aws-cli`` standard configuration.

Usage::

    $ aws2fa [profile]
    2FA device serial number for profile 'default': arn:aws:iam::123456789:mfa/username
    2FA code: 123456
    Sucesss! Your token will expire on: 2017-06-04 09:08:27+00:00

Now you can use ``aws-cli`` or any ``aws`` library which uses ``~/.aws/credentials`` standard configuration.


Features
---------

* ``aws2fa`` respects ``aws-cli`` configuration. No magic, no duplicated credentials.
* Full integration with ``aws-cli`` profiles
* Smooth device handling
* Super minimal implementation


Installation
--------------

Simply run::

    $ pip install aws2fa


We assume you have previously installed and configured ``aws-cli``::

    $ pip install awscli
    $ awscli configure


Configuration conventions
---------------------------

``aws2fa`` handles this automatically for you. You don't need to worry about this.

* ``$profile::source-profile``: A profile with this name will be created to store your original credentials.
* ``$profile``: This profile will contain the temporal credentials for the duration of your session.

Contribute
-----------

* Fork the repository on GitHub.
* Write a test which shows that the bug was fixed or that the feature works as expected.

  - Use ``tox`` command to run all the tests in all locally available python version.

* Send a pull request and bug the maintainer until it gets merged and published. :).


AWS configuration
------------------

* Create a user in the IAM console
* Create and attach a policy which defines a explicit deny to all actions and resources if a multi-factor device is not present (`Documentation about explicit-deny <http://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html#AccessPolicyLanguage_Interplay>`_.)::

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Deny",
                "Action": "*",
                "Resource": "*",
                "Condition": {
                    "BoolIfExists": {
                        "aws:MultiFactorAuthPresent": false
                    }
                }
            }
        ]
    }

* Attach any other custom or aws-provided policy to the user that you want allow access to.


Alternatives
-------------

Another option would be to use what Andreas Wittig describes in his article `Improve AWS security: protect your keys with ease <https://cloudonaut.io/improve-aws-security-protect-your-keys-with-ease/>`_. The idea behind, is to instead of doing a explicit-deny on all resources or actions (if a 2fa token has not been used), you just allow the user to assume a role if a 2fa device is present.

Then, after creating different roles, you can configure ``aws-cli`` to assume certain roles when you use certain profiles.

I can see why this approach is interesting for many cases, but I believe following the explicit deny approach is more straight forward for many others.


Helpful Links
-------------

* http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html
* https://cloudonaut.io/improve-aws-security-protect-your-keys-with-ease/
