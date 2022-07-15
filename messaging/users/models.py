# django setup
import sys
import os
import pathlib

os.environ["DJANGO_SETTINGS_MODULE"] = "messaging.web.src.config.settings"
parent_path = pathlib.Path(__file__).parent.parent
django_path = parent_path.joinpath("web", "src")
sys.path = sys.path + [ django_path.as_posix() ]
print(sys.path)

from messaging.web.src.apps.core.models import Device  # type: ignore
from messaging.web.src.apps.accounts.models import User  # type: ignore
