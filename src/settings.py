# -*- coding: utf-8 -*-
# Django settings used as base for developing wirecloud.

from os import path
from wirecloud.commons.utils.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

DEBUG = True
TEMPLATE_DEBUG = DEBUG
COMPRESS = not DEBUG
COMPRESS_OFFLINE = not DEBUG
USE_XSENDFILE = False

BASEDIR = path.dirname(path.abspath(__file__))
APPEND_SLASH = False

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',      # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': path.join(BASEDIR, 'wirecloud.db'),  # Or path to database file if using sqlite3.
        'TEST_NAME': path.join(BASEDIR, 'test_wirecloud.db'),
        'USER': '',                                  # Not used with sqlite3.
        'PASSWORD': '',                              # Not used with sqlite3.
        'HOST': '',                                  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                                  # Set to empty string for default. Not used with sqlite3.
    },
}

# This setting has only effect in DJango 1.5+
# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

THEME_ACTIVE = "wirecloud.defaulttheme"

# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Madrid'
DATE_FORMAT = 'd/m/Y'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
LANGUAGE_CODE = 'en'
DEFAULT_LANGUAGE = 'browser'

LANGUAGES = (
    ('es', _('Spanish')),
    ('en', _('English')),
    ('pt', _('Portuguese')),
)

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

STATIC_URL = '/static/'
STATIC_ROOT = path.join(BASEDIR, 'static')
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_OUTPUT_DIR = 'cache'
COMPRESS_JS_FILTERS = (
    'compressor.filters.jsmin.JSMinFilter',
    'wirecloud.platform.compressor_filters.JSUseStrictFilter',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '15=7f)g=)&spodi3bg8%&4fqt%f3rpg%b$-aer5*#a*(rqm79e'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'wirecloud.platform.themes.load_template_source',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'wirecloud.commons.middleware.URLMiddleware',
)

URL_MIDDLEWARE_CLASSES = {
    'default': (
        'django.middleware.gzip.GZipMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.locale.LocaleMiddleware',
        'wirecloud.commons.middleware.ConditionalGetMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ),
    'api': (
        'django.middleware.gzip.GZipMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.locale.LocaleMiddleware',
        'wirecloud.commons.middleware.ConditionalGetMiddleware',
        'wirecloud.commons.middleware.AuthenticationMiddleware',
    ),
    'proxy': (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
    )
}

ROOT_URLCONF = 'urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'wirecloud.commons',
    'wirecloud.catalogue',
    'wirecloud.platform',
    'wirecloud.oauth2provider',
    'wirecloud.fiware',
    'south',
    'compressor',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.static',
    'wirecloud.platform.themes.active_theme_context_processor',
)

STATICFILES_FINDERS = (
    'wirecloud.platform.themes.ActiveThemeFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

SESSION_COOKIE_AGE = 5184000  # 2 months

SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Login/logout URLs
LOGIN_URL = reverse_lazy('login')
LOGOUT_URL = reverse_lazy('wirecloud.root')
LOGIN_REDIRECT_URL = reverse_lazy('wirecloud.root')

#Authentication
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

# WGT deployment dirs
CATALOGUE_MEDIA_ROOT = path.join(BASEDIR, 'catalogue', 'media')
GADGETS_DEPLOYMENT_DIR = path.join(BASEDIR, 'deployment', 'widgets')

#SESSION_COOKIE_DOMAIN = '.domain'

# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'wirecloud.platform.cache.backends.locmem.LocMemCache',
        'OPTIONS': {
            'MAX_ENTRIES': 3000,
        },
    }
}

WORKSPACE_MANAGERS = (
    'wirecloud.platform.workspace.workspace_managers.OrganizationWorkspaceManager',
)

#WIRECLOUD_PLUGINS = (
#    'wirecloud.oauth2provider.plugins.OAuth2ProviderPlugin',
#    'wirecloud.fiware.plugins.FiWarePlugin',
#)

FORCE_SCRIPT_NAME = ""

NOT_PROXY_FOR = ['localhost', '127.0.0.1']

PROXY_PROCESSORS = (
#    'wirecloud.proxy.processors.FixServletBugsProcessor',
    'wirecloud.proxy.processors.SecureDataProcessor',
)

# External settings configuration
try:
    from local_settings import *  # pyflakes:ignore
except ImportError:
    pass
