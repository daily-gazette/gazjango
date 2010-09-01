# Django settings for gazjango project.

from settings_secret import *
# Defines:
#   SECRET_KEY
#   AKISMET_API_KEY
#   GMAPS_API_KEY
#   RECAPTCHA_{PRIVATE,PUBLIC}_KEY
#   FACEBOOK_LOGIN_{APP_ID,API_KEY,SECRET}
#   FLICKR_{API,SECRET,USRID}

import os
BASE = os.path.dirname(__file__)

TEMPLATE_DEBUG = DEBUG = True

ADMINS = (
    ('Dougal Sutherland', 'admin@daily.swarthmore.edu'),
)
MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = BASE + '/uploads'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/uploads/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
    # 'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'gazjango.facebook_connect.middleware.FacebookConnectMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'gazjango.stackedpages.middleware.StackedPageFallbackMiddleware',
)

ROOT_URLCONF = 'gazjango.urls'

TEMPLATE_DIRS = (
    BASE + '/templates'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'gazjango.facebook_connect.context_processors.api_keys',
    'gazjango.facebook_connect.context_processors.login_status',
    'gazjango.options.context_processors.headerbar',
    'gazjango.comments.context_processors.popular_comments',
    'gazjango.issues.context_processors.weather_joke',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.humanize',
    'django.contrib.markup',
    
    'imagekit',
    'registration',

    'gazjango.accounts',
    'gazjango.ads',
    'gazjango.announcements',
    'gazjango.articles',
    'gazjango.athletics',
    'gazjango.blogroll',
    'gazjango.books',
    'gazjango.comments',
    'gazjango.facebook_connect',
    'gazjango.issues',
    'gazjango.jobs',
    'gazjango.media',
    'gazjango.misc',
    'gazjango.options',
    'gazjango.polls',
    'gazjango.reviews',
    'gazjango.scrapers',
    'gazjango.screw',
    'gazjango.housing',
    'gazjango.stackedpages',
    'gazjango.subscriptions',
    'gazjango.tagging',
    'gazjango.community',
    'gazjango.popular',
)

AUTH_PROFILE_MODULE = "accounts.userprofile"
LOGIN_REDIRECT_URL = "/"

ACCOUNT_ACTIVATION_DAYS = 4

SWARTHMORE_IP_BLOCK = '130.58.'

LOCAL_JQUERY = False

# Settings for the community app
AGRO_SETTINGS = {
    # these are the names of the files in your sources directory
    'source_list': ('twitter','delicious','flickr'),

    # here is where you add login details
    # for a single user, these will be strings
    # for multiple users, it's a tuple of user information
    # flickr requires a tuple, even for single users.
    'accounts': {
        'twitter':'swatgazette',
        'delicious':'swarthmore',
        'flickr':(('arador', '35285883@N00'),)
    },
    
    # for services that require an API key, they are added like so
    # note that last.fm also requires a secret, so we add its api key and secret as a tuple
    'api_keys': {
        'flickr': FLICKR_API,
    },
}
