import logging

from django.contrib.auth import get_user_model


logger = logging.getLogger(__name__)
User = get_user_model()
