"""Development settings for portfolio app."""

from .base import *


DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'dh8bvlv8oh7il',
        'USER': 'ycgqszqhxrrgfs',
        'PASSWORD': '236f1b8d9017de301cb563d193b537'
                    'bddd5a20d46429b662954706304cb98c0c',
        'HOST': 'ec2-174-129-255-26.compute-1.amazonaws.com',
        'PORT': '5432',
    }
}
