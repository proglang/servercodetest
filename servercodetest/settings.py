from .util import to_bool, to_int, env, etob, etoi

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "t-_(o@s=k&+6uzkc_9cx5^z3mhrf47$_@hakq+)9162u@$h+q&"

#! ##########################################################################
#! ################################ Settings ################################
#! ##########################################################################

# | Path to App
DJANGO_BASE_URL_PATH = env("SCT_BASE_URL_PATH", "")

# | Log level
# Possible Values:
#   CRITICAL, ERROR, WARNING, INFO, DEBUG, TRACE, NOTSET
LOG_LEVEL = env("SCT_LOG_LEVEL", "WARNING")

# | timeout of API requests
TIMEOUT = etoi("SCT_TIMEOUT", 60, 30, 60 * 10)

# | Debug mode
#! SECURITY WARNING: don't run with debug turned on in production!
DEBUG = etob("SCT_DEBUG")

# | Docker
DOCKER_ENABLED = etob("SCT_DOCKER")
DOCKER_NETWORK = env("SCT_DOCKER_NETWORK")
DOCKER_PREFIX = env("SCT_DOCKER_PREFIX", "sct")


# | DATABASE
DATABASE_NAME = env("SCT_DATABASE_NAME")
DATABASE_USER = env("SCT_DATABASE_USER")
DATABASE_PASSWORD = env("SCT_DATABASE_PASSWORD")
DATABASE_HOST = env("SCT_DATABASE_HOST", "localhost")
DATABASE_PORT = etoi("SCT_DATABASE_PORT", 3306)

# should not be used
# this is used for unit testing
USED_SETTINGS = env("SCT_DJANGO_SETTING", "main")


import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.join(ROOT_DIR, "servercodetest")
STATIC_ROOT = os.path.join(ROOT_DIR, "deploy", "static")
PLUGIN_DIR = os.path.join(ROOT_DIR, "plugins")

#! ##########################################################################
#! ##########################################################################
#! ######################## DO NOT CHANGE CODE BELOW ########################
#! ##########################################################################
#! ##########################################################################
"""
For more information on Django settings, see
https://docs.djangoproject.com/en/3.0/topics/settings/
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

DJANGO_BASE_URL_PATH = DJANGO_BASE_URL_PATH.strip().strip("/")
if DJANGO_BASE_URL_PATH != "":
    DJANGO_BASE_URL_PATH = f"/{DJANGO_BASE_URL_PATH}"
    FORCE_SCRIPT_NAME = DJANGO_BASE_URL_PATH
    USE_X_FORWARDED_HOST = True

ALLOWED_HOSTS = [
    "*",
]


# Application definition

INSTALLED_APPS = [
    "django.contrib.auth",
    "app.apps.AppConfig",

    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    'django.middleware.locale.LocaleMiddleware',
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "servercodetest.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [STATIC_ROOT, "templates",],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "servercodetest.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

AVAILABLE_DB = {
    "main": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": DATABASE_NAME,
        "HOST": DATABASE_HOST,
        "PORT": DATABASE_PORT,
        "USER": DATABASE_USER,
        "PASSWORD": DATABASE_PASSWORD,
        "CHARSET": "utf8",
        "COLLATION": "utf8_general_ci",
    },
    "test": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(ROOT_DIR, ".pytest_cache", "db.test.sqlite3"),
    },
}
DATABASES = {"default": AVAILABLE_DB.get(USED_SETTINGS, "main")}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/
LANGUAGES = [
    ('de', 'German'),
    ('en', 'English'),
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_SUFFIX = "/static/"
STATIC_URL = DJANGO_BASE_URL_PATH + STATIC_SUFFIX
STATICFILES_DIRS = []

