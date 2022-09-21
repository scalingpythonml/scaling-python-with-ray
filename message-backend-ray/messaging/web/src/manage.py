#!/usr/bin/env python3

import os
import sys


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    os.environ.setdefault("DJANGO_CONFIGURATION", os.environ.get("__ENV__"))

    from configurations.management import (
        execute_from_command_line,
    )  # NOQA isort:skip

    execute_from_command_line(sys.argv)
