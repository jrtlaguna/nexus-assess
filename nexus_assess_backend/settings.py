import os
from datetime import timedelta
from pathlib import Path

import environ
from celery.schedules import crontab

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
env.read_env(os.path.join(BASE_DIR, ".env"))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("HOST", default=["*"])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if DEBUG:
    ALLOWED_HOSTS.append("*")

SITE_ID = 1


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]


THIRD_PARTY_APPS = [
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "django_celery_beat",
    "django_celery_results",
    "corsheaders",
    "django_extensions",
    "drf_yasg",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "rest_framework",
    "rest_framework.authtoken",
    "admin_auto_filters",
    "admin_reorder",
]

LOCAL_APPS = [
    "core",
    "users.apps.UsersConfig",
    "requirements.apps.RequirementsConfig",
    "assessments.apps.AssessmentsConfig",
]

INSTALLED_APPS += THIRD_PARTY_APPS + LOCAL_APPS


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "core.middleware.ModelAdminReorderWithNav",
]

ROOT_URLCONF = "nexus_assess_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "debug": True,
        },
    },
]

WSGI_APPLICATION = "nexus_assess_backend.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

if env.str("DATABASE_URL", default=None):
    DATABASES = {"default": env.db()}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Primarily used for emails. We want to save datetimes in UTC,
# but we want to display datetimes in emails in EST
DEFAULT_TIMEZONE = "US/Eastern"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)
ACCOUNT_USER_MODEL_USERNAME_FIELD = "email"


# Logging
# https://docs.djangoproject.com/en/4.1/topics/logging/

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": env.path(
                "ERROR_LOG_PATH", default=os.path.join(BASE_DIR, "error.log")
            ),
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,
            "formatter": "standard",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "django.request": {
            "handlers": ["mail_admins", "file"],
            "level": "ERROR",
        },
    },
}


# Email

SENDGRID_API_KEY = env.str("SENDGRID_API_KEY", None)
EMAIL_BACKEND = env.str(
    "DEFAULT_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)

if SENDGRID_API_KEY:
    EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"

# EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
# EMAIL_FILE_PATH = os.path.join(BASE_DIR, "tmp", "email")

DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL", "no-reply@nexusgroup.com")
SENDGRID_SANDBOX_MODE_IN_DEBUG = env.bool("SENDGRID_SANDBOX_MODE_IN_DEBUG", False)
if SENDGRID_SANDBOX_MODE_IN_DEBUG:
    SENDGRID_ECHO_TO_STDOUT = True

FRONTEND_URL = env.str("FRONTEND_URL", "http://localhost:3000")
BACKEND_URL = env.str("BACKEND_URL", "http://localhost:8000")


# Allauth

ACCOUNT_ADAPTER = "users.adapter.AccountAdapter"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = False
ACCOUNT_EMAIL_SUBJECT_PREFIX = ""
ACCOUNT_UNIQUE_EMAIL = True
LOGIN_URL = "/login"
LOGIN_REDIRECT_URL = "/"
OLD_PASSWORD_FIELD_ENABLED = True

# S3
FILE_STORAGE_S3 = env.bool("FILE_STORAGE_S3", default=False)
AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID", None)
AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY", None)
AWS_STORAGE_BUCKET_NAME = env.str("AWS_STORAGE_BUCKET_NAME", None)
AWS_S3_REGION_NAME = env.str("AWS_S3_REGION_NAME", None)
STORAGES = {
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
}

if FILE_STORAGE_S3:
    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
    }


# REST Framework

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        # "rest_framework.authentication.SessionAuthentication",
        # "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.TokenAuthentication",
        "dj_rest_auth.jwt_auth.JWTCookieAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 6,
}


# REST Auth
REST_AUTH = {
    "OLD_PASSWORD_FIELD_ENABLED": True,
    "PASSWORD_CHANGE_SERIALIZER": "users.api.v1.serializers.PasswordChangeSerializer",
    "PASSWORD_RESET_SERIALIZER": "users.api.v1.serializers.PasswordResetSerializer",
    "USER_DETAILS_SERIALIZER": "users.api.v1.serializers.UserSerializer",
}


# JWT
REST_USE_JWT = True
JWT_AUTH_COOKIE = "jwt-auth"
JWT_AUTH_REFRESH_COOKIE = "jwt-refresh-token"
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
}


# Swagger

SWAGGER_SETTINGS = {
    "DEFAULT_INFO": f"{ROOT_URLCONF}.api_info",
}


# CORS

CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=["http://127.0.0.1:3000", "http://localhost:3000"],
)


# Celery

CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_CACHE_BACKEND = "django-cache"
CELERY_RESULT_BACKEND = "django-db"
CELERY_RESULT_EXTENDED = True
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_TRACK_STARTED = True
CELERY_TIMEZONE = "UTC"
CELERY_BEAT_SCHEDULE = {}

# Django Admin Reorder

ADMIN_REORDER = (
    "user",
    {
        "app": "users",
        "label": "Accounts",
        "models": (
            "users.User",
            "users.Company",
            "auth.Group",
        ),
    },
    {
        "app": "assessments",
        "label": "Compliance Criticality Assessment",
        "models": (
            "assessments.ComplianceCriticalityAssessment",
            "assessments.Report",
            "assessments.ReviewComment",
            "assessments.AssessmentExport",
        ),
    },
    {
        "app": "requirements",
        "label": "Source Table",
        "models": (
            "requirements.Requirement",
            "requirements.RequirementCategory",
            "requirements.Compliance",
            "requirements.ComplianceCategory",
            "requirements.Reference",
            "requirements.ReferencePolicy",
            "requirements.ReferenceCategory",
        ),
    },
    {
        "app": "auth",
        "label": "Authentication",
        "models": (
            "authtoken.TokenProxy",
            "account.EmailAddress",
            "socialaccount.SocialAccount",
            "socialaccount.SocialApp",
            "socialaccount.SocialToken",
        ),
    },
    {
        "app": "sites",
        "label": "Settings",
        "models": (
            "sites.Site",
            "django_celery_results.TaskResult",
            "django_celery_beat.CrontabSchedule",
            "django_celery_beat.IntervalSchedule",
            "django_celery_results.GroupResult",
        ),
    },
)
