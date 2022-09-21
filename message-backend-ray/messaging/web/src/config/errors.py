from django.http import JsonResponse

from rest_framework import status


def forbidden(request, *args, **kwargs):
    """
    Generic 403 error handler.
    """
    data = {"error": "Forbidden (403)"}
    return JsonResponse(data, status=status.HTTP_403_FORBIDDEN)
