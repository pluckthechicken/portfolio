"""Portfolio production settings."""

from base import *

DEBUG = False

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'stocks.neoformit.com',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'portfolio',
        'USER': 'portfolio',
        'PASSWORD': 'f475y4i85467',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

STATIC_ROOT = os.path.join(
    BASE_DIR,
    'portfolio',
    'static',
)
