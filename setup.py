from setuptools import setup, find_packages

setup(
    name='message-backend-ray',
    version='0.0.1',
    author='Holden Karau',
    author_email='holden@pigscanfly.ca',
    packages=['message-backend-ray'],
    url='https://github.com/scalingpythonml/scaling-python-with-ray',
    license='LICENSE.txt',
    description='Message backend, in Python using Ray.',
    long_description='',
    install_requires=[
        'unittest2',
        'ray==1.13.0',
        'protobuf==4.21.2'
    ],
    test_requires=[
        'nose',
        'coverage',
        'unittest2'
    ],
)
