#!/usr/bin/env python
import os
import sys


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise

    ## Connect to mongo
    try:
        import mongoengine
        from django.conf import settings

        mongoengine.connect(settings.MONGO_SETTINGS['database'])
    except ImportError:
        raise ImportError("Couldn't import mongoengine.")

    execute_from_command_line(sys.argv)
