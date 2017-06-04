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


Helpful Links
-------------

* http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html
* https://cloudonaut.io/improve-aws-security-protect-your-keys-with-ease/
