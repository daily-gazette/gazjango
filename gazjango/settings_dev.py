from settings_base import *

DATABASE_ENGINE   = 'sqlite3'
#For the importer to work, this needs to be an absolute path.
DATABASE_NAME     = BASE + '/development.db'
DATABASE_USER     = ''
DATABASE_PASSWORD = ''
DATABASE_HOST     = ''
DATABASE_PORT     = ''

CACHE_BACKEND = 'locmem:///'

ADMIN_MEDIA_PATH = '/Library/Python/2.5/site-packages/django/contrib/admin/media/'
