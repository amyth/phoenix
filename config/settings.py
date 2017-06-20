"""
Django settings for phoenix project.

Generated by 'django-admin startproject' using Django 1.10.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
from campaign_permissions import *
from .log_settings import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@-76h9fd9r5j&n1jk+_3zqn@1^e^=a272m0*+20xnwm72rdq4%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['phoenix.shine.com', '*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.backend',
    'rules',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'staticfiles')]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')


## mongoengine
MONGO_SETTINGS = {
    'database': 'phoenix',
}

LOG_DATA_DIR = "/data/logs"
LOGIN_URL = "/login/"
ADMIN_MEDIA_PREFIX = '/static/'
LOGIN_REDIRECT_URL = '/'
FERNET_DECRYPT_KEY = 'F8lZb_92t4prgjLRIgIkdA5_2XSX-h0aPnElWROUyTA='

#MYSQL_PARSER_SETTINGS = {
#    'host': '172.22.67.126',
#    'port': 3306,
#    'username': 'phoenix',
#    'password': 'Phoenix@313',
#    'database': 'phoenix_dev'
#}
MYSQL_PARSER_SETTINGS = {
    'host': '127.0.0.1',
    'port': 3306,
    'username': 'root',
    'password': 'Puresy307',
    'database': 'phoenix_dev'
}

##### EMAIL SETTINGS ##################################

ADMINS = (
    ('Amyth', 'aroras.official@gmail.com'),
    ('Vijay', 'vijay.mendiratta@hindustantimes.com'),
    ('Ishank', 'ishank.mahana@hindustantimes.com'),
    ('Tanvi', 'tanvi.arora@hindustantimes.com'),
)
EMAIL_HOST = '172.22.65.55'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
SERVER_EMAIL = 'Phoenix <phoenix@shine.com>'
DEFAULT_FROM_EMAIL = SERVER_EMAIL

#######################################################


try:
    from .personal import *
except ImportError as err:
    # Personal settings file does not exist
    # Skip and use generic settings.
    pass


try:
    import mongoengine
    mongoengine.connect(MONGO_SETTINGS['database'])
except ImportError:
    raise ImportError("Couldn't import mongoengine.")
