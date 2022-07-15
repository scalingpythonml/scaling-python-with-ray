# django setup
import sys
import os
import pathlib

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
parent_path = pathlib.Path(__file__).parent.parent
django_path = parent_path.joinpath("web", "src")
sys.path = sys.path + [ django_path.as_posix() ]

import django
django.setup()

from apps.accounts.models import User  # type: ignore
from apps.core.models import Device  # type: ignore
