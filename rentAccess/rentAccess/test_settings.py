import os
import environ
from pathlib import Path
from datetime import timedelta
from celery.schedules import crontab
from kombu import Exchange, Queue

# finding a root directory of the project
root = environ.Path(__file__) - 2

# setting roots for static, media, templates
templates_root = root('templates')

env = environ.Env()
# reading env file
environ.Env.read_env(env_file=root('.env'))
# site root points to rentAccess root folder
SITE_ROOT = root()
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
DEBUG = env.bool('DEBUG', default=False)
SECRET_KEY = env.str('SECRET_KEY')
ALLOWED_HOSTS = env("ALLOWED_HOSTS").split(",")
ADMINS = env.list("ADMINS", default=[('Yury Borodin', 'yuiborodin@lockandrent.ru')])

CORS_ORIGIN_ALLOW_ALL = env.bool('CORS_ORIGIN_ALLOW_ALL', default=True)

CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS')

LOGGING = {
	'version': 1,
	'disable_existing_loggers': True,
	'formatters': {
		'file': {
			'()': 'django.utils.log.ServerFormatter',
			'format': '[{server_time}] {levelname} {message}',
			# 'datefmt': '%Y-%m-%d %H:%M:%S'
			'style': '{'
		},
		'request_file': {
			'()': 'django.utils.log.ServerFormatter',
			'format': "[{server_time}] {levelname} status_code={status_code} user_id={request.user.id} META={request.META}",
			# 'datefmt': '%Y-%m-%d %H:%M:%S'
			'style': '{'
		}
	},
	'handlers': {
		'console': {
			'class': 'logging.StreamHandler',
		},
		'server_logs_info': {
			'delay': True,
			'level': 'INFO',
			'class': 'logging.handlers.TimedRotatingFileHandler',
			'when': 'midnight',
			'interval': 1,
			'formatter': 'file',
			'filename': env.str('LOG_ROOT')+'server.log',

		},
		'request_logs_info': {
			'delay': True,
			'level': 'INFO',
			'class': 'logging.handlers.TimedRotatingFileHandler',
			'when': 'midnight',
			'interval': 1,
			'formatter': 'request_file',
			'filename': env.str('LOG_ROOT')+'requests.log',

		},
		'template_logs_info': {
			'level': 'INFO',
			'delay': True,
			'class': 'logging.handlers.TimedRotatingFileHandler',
			'when': 'midnight',
			'interval': 1,
			'formatter': 'file',
			'filename': env.str('LOG_ROOT')+'templates.log',

		},
		'security_logs_info': {
			'level': 'INFO',
			'delay': True,
			'class': 'logging.handlers.TimedRotatingFileHandler',
			'when': 'midnight',
			'interval': 1,
			'formatter': 'file',
			'filename': env.str('LOG_ROOT')+'security.log',

		},
		'properties_images': {
			'level': 'INFO',
			'delay': True,
			'class': 'logging.handlers.TimedRotatingFileHandler',
			'when': 'midnight',
			'interval': 1,
			'formatter': 'file',
			'filename': env.str('LOG_ROOT')+'images.log',

		},
		'properties_crud_info_file': {
			'level': 'INFO',
			'delay': True,
			'class': 'logging.handlers.TimedRotatingFileHandler',
			'when': 'midnight',
			'interval': 1,
			'formatter': 'file',
			'filename': env.str('LOG_ROOT')+'crud.log'
		},
		'properties_owners_info_file': {
			'level': 'INFO',
			'delay': True,
			'class': 'logging.handlers.TimedRotatingFileHandler',
			'when': 'midnight',
			'interval': 1,
			'formatter': 'file',
			'filename': env.str('LOG_ROOT')+'owners.log'
		},
		'properties_locks_info_file': {
			'level': 'INFO',
			'delay': True,
			'class': 'logging.handlers.TimedRotatingFileHandler',
			'when': 'midnight',
			'interval': 1,
			'formatter': 'file',
			'filename': env.str('LOG_ROOT')+'locks.log'
		},
		'properties_bookings_info_file': {
			'level': 'INFO',
			'delay': True,
			'class': 'logging.handlers.TimedRotatingFileHandler',
			'when': 'midnight',
			'interval': 1,
			'formatter': 'file',
			'filename': env.str('LOG_ROOT')+'bookings.log'
		}

	},
	'loggers': {
		'rentAccess.properties.crud.info': {
			'level': 'INFO',
			'handlers': ['properties_crud_info_file']
		},
		'rentAccess.properties.owners.info': {
			'level': 'INFO',
			'handlers': ['properties_owners_info_file']
		},
		'rentAccess.properties.bookings.info': {
			'level': 'INFO',
			'handlers': ['properties_bookings_info_file']
		},
		'rentAccess.properties.locks.info': {
			'level': 'INFO',
			'handlers': ['properties_locks_info_file']
		},
		'rentAccess.properties.images.info': {
			'level': 'INFO',
			'handlers': ['properties_images']
		},
		'django.server': {
			'handlers': ['server_logs_info'],
			'level': 'INFO'
		},
		'django.request': {
			'handlers': ['request_logs_info'],
			'level': 'INFO'
		},
		'django.template': {
			'handlers': ['template_logs_info'],
			'level': 'INFO'
		},
		'django.security.*': {
			'handlers': ['security_logs_info'],
			'level': 'INFO'
		}
	}
}

INSTALLED_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'rest_framework',
	'rest_framework_swagger',
	'rest_framework_simplejwt.token_blacklist',
	'watchman',
	'timezone_field',
	'properties',
	'bookings',
	'organisations',
	'jwtauth',
	'userAccount',
	'corsheaders',
	'common',
	'register',
	'keys',
	'schedule',
	'locks',
	'checkAccess',
]

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'corsheaders.middleware.CorsMiddleware',

]
AUTH_USER_MODEL = 'userAccount.CustomUser'

ROOT_URLCONF = 'rentAccess.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': ['templates'],
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

WSGI_APPLICATION = 'rentAccess.wsgi.application'


# Databases
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': 'db.sqlite3',
	}
}

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DEFAULT_RENDERER_CLASSES = (
	'rest_framework.renderers.JSONRenderer',
)

################################################
# when DEBUG == True DRF will render errors as html pages
if DEBUG:
	DEFAULT_RENDERER_CLASSES = DEFAULT_RENDERER_CLASSES + (
		'rest_framework.renderers.BrowsableAPIRenderer',
	)

REST_FRAMEWORK = {
	'DEFAULT_PERMISSION_CLASSES': [
		'rest_framework.permissions.IsAuthenticated',
	],
	"DEFAULT_PARSER_CLASSES": [
		"rest_framework.parsers.JSONParser",
	],
	'DEFAULT_THROTTLE_CLASSES': [
		'rest_framework.throttling.AnonRateThrottle',
		'rest_framework.throttling.UserRateThrottle'
	],
	'DEFAULT_THROTTLE_RATES': {
		'anon': '10000/day',
		'user': '10000/day'
	},
	'DATETIME_FORMAT': "%Y-%m-%dT%H:%M:%S%z",
	'DEFAULT_AUTHENTICATION_CLASSES': [
		'rest_framework_simplejwt.authentication.JWTAuthentication',
		'rest_framework.authentication.SessionAuthentication',
	],

	'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
	'PAGE_SIZE': 50,

	'EXCEPTION_HANDLER': 'rentAccess.error_handler.custom_exception_handler',
	'DEFAULT_RENDERER_CLASSES': DEFAULT_RENDERER_CLASSES
}
if DEBUG:
	SIMPLE_JWT = {
		'ACCESS_TOKEN_LIFETIME': timedelta(minutes=3600),
		'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
		'ROTATE_REFRESH_TOKENS': False,
		'BLACKLIST_AFTER_ROTATION': True,

		'ALGORITHM': 'HS256',
		'SIGNING_KEY': SECRET_KEY,
		'VERIFYING_KEY': None,
		'AUDIENCE': None,
		'ISSUER': None,

		'AUTH_HEADER_TYPES': ('Bearer',),
		'USER_ID_FIELD': 'id',
		'USER_ID_CLAIM': 'user_id',

		'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
		'TOKEN_TYPE_CLAIM': 'token_type',

		'JTI_CLAIM': 'jti',

		'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
		'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
		'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
	}

else:
	################################################
	# Media root and url definitions

	SIMPLE_JWT = {
		'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
		'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
		'ROTATE_REFRESH_TOKENS': False,
		'BLACKLIST_AFTER_ROTATION': True,

		'ALGORITHM': 'HS256',
		'SIGNING_KEY': SECRET_KEY,
		'VERIFYING_KEY': None,
		'AUDIENCE': None,
		'ISSUER': None,

		'AUTH_HEADER_TYPES': ('Bearer',),
		'USER_ID_FIELD': 'id',
		'USER_ID_CLAIM': 'user_id',

		'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
		'TOKEN_TYPE_CLAIM': 'token_type',

		'JTI_CLAIM': 'jti',

		'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
		'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
		'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
	}
MEDIA_ROOT = os.path.join('media')
MEDIA_URL = '/media/'

# Static root and file definitions
STATICFILES_DIRS = [
	root("static"),
]
STATIC_URL = '/static/'
STATIC_ROOT = '/static/'
# CELERY CONFIG

CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", default='redis://127.0.0.1:6379')
CELERY_RESULT_BACKEND = env.str('CELERY_RESULT_BACKEND', default='redis://127.0.0.1:6379')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Moscow'

# default_exchange = Exchange('default', type='direct')
# priority_exchange = Exchange('priority_queue', type='direct')

# CELERY_QUEUES = (
#    Queue('default', default_exchange, routing_key='default', consumer_arguments={'x-priority': 0}),
#    Queue('priority_queue', priority_exchange, routing_key='priority_queue', consumer_arguments={'x-priority': 10}),
# )
# CELERY_ROUTES = ({'jwtauth.tasks.test_task': {
#                        'queue': 'priority_queue',
#                        'routing_key': 'priority_queue'
#                }}, )
# CELERY_DEFAULT_QUEUE = 'default'
# CELERY_DEFAULT_EXCHANGE = 'default'
# CELERY_DEFAULT_ROUTING_KEY = 'default'

# EMAIL SETTINGS
SERVER_EMAIL = 'server@lockandrent.ru'
EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')

# TEMPLATE_PREVIEW_DIR = root('templates')
