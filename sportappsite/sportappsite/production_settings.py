"""
Django settings for sportappsite project.

Generated by 'django-admin startproject' using Django 1.9.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import datetime

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

with open(os.path.join(BASE_DIR, "secret-key.txt")) as f:
    SECRET_KEY = f.read().strip()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    "www.fanaboard.com",
    "fanaboard.com",
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(filename)s "
            "%(module)s %(funcName)s %(process)d %(processName)s "
            ":: %(message)s"
        }
    },
    "handlers": {
        "django-file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "formatter": "verbose",
            "filename": os.path.join(BASE_DIR, "../logs/django.log"),
        },
        "live-prediction-scoring-file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "formatter": "verbose",
            "filename": os.path.join(BASE_DIR, "../logs/live-prediction-scoring.log"),
        },
        "rules-execution-file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "formatter": "verbose",
            "filename": os.path.join(BASE_DIR, "../logs/rules-execution.log"),
        },
        "predictions-conversions-file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "formatter": "verbose",
            "filename": os.path.join(BASE_DIR, "../logs/predictions-conversions.log"),
        },
        "live-scores-ball-by-ball-file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "formatter": "verbose",
            "filename": os.path.join(BASE_DIR, "../logs/live-scores-ball-by-ball.log"),
        },
        "auto-jobs-file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "formatter": "verbose",
            "filename": os.path.join(BASE_DIR, "../logs/auto-jobs.log"),
        },
        "p-a-computations-file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "verbose",
            "filename": os.path.join(BASE_DIR, "../logs/p-a-computations.log"),
            "maxBytes": 104857600,
            "backupCount": 10,
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "include_html": True,
        },
    },
    "loggers": {
        "django": {"handlers": ["django-file"], "level": "INFO", "propagate": True,},
        "prediction_scoring": {
            "handlers": ["live-prediction-scoring-file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "rules_execution": {
            "handlers": ["rules-execution-file"],
            "level": "INFO",
            "propagate": False,
        },
        "predictions_conversions": {
            "handlers": ["predictions-conversions-file"],
            "level": "INFO",
            "propagate": False,
        },
        "live_scores.ball_by_ball": {
            "handlers": ["live-scores-ball-by-ball-file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "auto_jobs": {
            "handlers": ["auto-jobs-file"],
            "level": "INFO",
            "propagate": False,
        },
        "p_a_computations": {
            "handlers": ["p-a-computations-file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# Application definition

INSTALLED_APPS = [
    "predictions.apps.PredictionsConfig",
    "members.apps.MembersConfig",
    "stats.apps.StatsConfig",
    "fixtures.apps.FixturesConfig",
    "scoring.apps.ScoringConfig",
    "imports.apps.ImportsConfig",
    "rules.apps.RulesConfig",
    "drf_api.apps.DrfApiConfig",
    "configurations.apps.ConfigurationsConfig",
    "live_scores.apps.LiveScoresConfig",
    "DynamicContent.apps.DynamiccontentConfig",
    "app_media.apps.AppMediaConfig",
    "rewards.apps.RewardsConfig",
    "securities.apps.SecuritiesConfig",
    "auto_jobs.apps.AutoJobsConfig",
    "grappelli",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "reversion",
    "django_summernote",
    "django_q",
    "rest_framework",
    "cacheops",
    "captcha",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "sportappsite.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "sportappsite.wsgi.application"

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
with open(os.path.join(BASE_DIR, "db-password.txt")) as f:
    DB_PASSWD = f.read().strip()

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "cricket",
        "USER": "cricket_user",
        "PASSWORD": DB_PASSWD,
        "HOST": "localhost",
        "PORT": "",
    }
}


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,  # in seconds
            "SOCKET_TIMEOUT": 5,  # in seconds,
            "IGNORE_EXCEPTIONS": True,
        },
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# https://github.com/Suor/django-cacheops
CACHEOPS_REDIS = {
    #  redis-server is on same machine
    "host": "localhost",
    #  default redis port
    "port": 6379,
    #  SELECT non-default redis database
    "db": 1,
    #  using separate redis db or redis instance
    #  is highly recommended
    #  connection timeout in seconds, optional
    "socket_timeout": 3,
}


CACHEOPS = {
    # Enable manual caching on all other models with default timeout of an hour
    # Use Post.objects.cache().get(...)
    #  or Tags.objects.filter(...).order_by(...).cache()
    # to cache particular ORM request.
    # Invalidation is still automatic
    "*.*": {"ops": (), "timeout": 60 * 60,},
}

CACHEOPS_DEGRADE_ON_FAILURE = True

# django_q
Q_CLUSTER = {
    "name": "DJRedis",
    "workers": 6,
    "timeout": None,
    "django_redis": "default",
    "save_limit": 1000,
}


REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated",],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "sportappsite.authentication.JWTSessionAuthentication",
    ),
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
}


CSRF_COOKIE_SAMESITE = "Strict"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

JWT_AUTH = {
    "JWT_ENCODE_HANDLER": "rest_framework_jwt.utils.jwt_encode_handler",
    "JWT_DECODE_HANDLER": "rest_framework_jwt.utils.jwt_decode_handler",
    "JWT_PAYLOAD_HANDLER": "sportappsite.utils.member_jwt_payload_handler",
    "JWT_PAYLOAD_GET_USER_ID_HANDLER": "rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler",
    "JWT_RESPONSE_PAYLOAD_HANDLER": "rest_framework_jwt.utils.jwt_response_payload_handler",
    "JWT_SECRET_KEY": SECRET_KEY,
    "JWT_GET_USER_SECRET_KEY": None,
    "JWT_PUBLIC_KEY": None,
    "JWT_PRIVATE_KEY": None,
    "JWT_ALGORITHM": "HS256",
    "JWT_VERIFY": True,
    "JWT_VERIFY_EXPIRATION": True,
    "JWT_LEEWAY": 0,
    "JWT_EXPIRATION_DELTA": datetime.timedelta(days=7),
    "JWT_AUDIENCE": None,
    "JWT_ISSUER": None,
    "JWT_ALLOW_REFRESH": False,
    "JWT_REFRESH_EXPIRATION_DELTA": datetime.timedelta(days=7),
    "JWT_AUTH_HEADER_PREFIX": "Bearer",
    "JWT_AUTH_COOKIE": None,
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static/")
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "python_field", "static"),
]


MEDIA_ROOT = os.path.join(STATIC_ROOT, "media/")
MEDIA_URL = "/static/media/"
MEDIA_DIR = {"app_media": "app-media/"}

# Grapelli config
GRAPPELLI_ADMIN_TITLE = "Cricket Matches -- Prediction and Analysis"

# Email
EMAIL_HOST = 'mail.sproutingstump.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = "noreply@fanaboard.com"
EMAIL_HOST_PASSWORD = "NoReply@123"
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_TIMEOUT = 10
DEFAULT_FROM_EMAIL = "noreply@fanaboard.com"

ADMINS = [
    ("Sawan", "sawan.vithlani@fanaboard.com"),
]


# Required by Django Summernote
X_FRAME_OPTIONS = "SAMEORIGIN"
