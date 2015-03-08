from .settings import *

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'rathena',
        'USER': 'travis',
        'PASSWORD': '',
        'HOST': '127.0.0.1'
    }
}
