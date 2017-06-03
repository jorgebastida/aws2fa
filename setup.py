import sys

from setuptools import setup, find_packages


install_requires = [
    'boto3>=1.4'
]


# as of Python >= 2.7 argparse module is maintained within Python.
extras_require = {
    ':python_version in "2.4, 2.5, 2.6"': ['argparse>=1.1.0'],
}


if 'bdist_wheel' not in sys.argv and sys.version_info < (2, 7):
    install_requires.append('argparse>1.1.0')


setup(
    name='aws2fa',
    version='0.0.1',
    url='https://github.com/jorgebastida/aws2fa',
    license='BSD',
    author='Jorge Bastida',
    author_email='me@jorgebastida.com',
    description='aws2fa is a simple command line tool to handle 2fa authentication respecting aws-cli standard patterns',
    keywords="aws 2fa auth authentication awscli",
    packages=find_packages(),
    platforms='any',
    install_requires=install_requires,
    extras_require=extras_require,
    test_suite='tests',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Utilities'
    ],
    entry_points={
        'console_scripts': [
            'aws2fa = aws2fa.bin:main',
        ]
    },
    zip_safe=False
)
