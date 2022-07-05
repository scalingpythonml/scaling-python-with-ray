from setuptools import setup  # type: ignore

setup(
    name='message-backend-ray',
    version='0.0.1',
    author='Holden Karau',
    author_email='holden@pigscanfly.ca',
    packages=['messaging'],
    url='https://github.com/scalingpythonml/scaling-python-with-ray',
    license='LICENSE.txt',
    description='Message backend, in Python using Ray.',
    long_description='',
    install_requires=[
        'unittest2',
        'ray',
        'protobuf<4.0.0,>=3.15.3'
    ]
)
