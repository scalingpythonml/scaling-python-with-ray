from django.conf import settings

from storages.backends.s3boto3 import S3Boto3Storage


class AWSStaticStorage(S3Boto3Storage):
    """
    Update default class to configure bucket
    and location for static files
    """

    bucket_name = settings.AWS_STATIC_BUCKET
    location = settings.AWS_STATIC_LOCATION
    querystring_auth = False


class AWSMediaStorage(S3Boto3Storage):
    """
    Update default class to configure bucket
    and location for media files
    """

    bucket_name = settings.AWS_MEDIA_BUCKET
    location = settings.AWS_MEDIA_LOCATION
    querystring_auth = False
