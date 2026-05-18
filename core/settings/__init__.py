import os
from dotenv import load_dotenv

load_dotenv()

env = os.getenv("DJANGO_ENV", "development")

if env == "production":
    from .production import *  # noqa
elif env == "testing":
    from .testing import *  # noqa
else:
    from .base import *  # noqa
