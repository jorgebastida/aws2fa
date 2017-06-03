aws2fa
=======

``aws2fa`` is a simple command to handle 2fa authentication respecting ``aws-cli`` standard configuration.

Simple usage::

    $ aws2fa [profile]

Features
---------

* ``aws2fa`` respects ``aws-cli`` configuration. No new magic or duplicated credentials
* Full integration with ``aws-cli`` profiles
* Smooth device handling
* Super minimal implementation


Configuration
--------------

The only new configuration file ``aws2fa`` creates is ``~/.aws/devices``. In this file, ``aws2fa`` stores the device serial number of your 2fa device for each of your profiles.

If the file is not present, or you are configuring a new profile, ``aws2fa`` will ask you for the serial number and store it in this file.


Contribute
-----------

* Fork the repository on GitHub.
* Write a test which shows that the bug was fixed or that the feature works as expected.

  - Use ``tox`` command to run all the tests in all locally available python version.

* Send a pull request and bug the maintainer until it gets merged and published. :).

For more instructions see `TESTING.rst`.


Helpful Links
-------------

* http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html
