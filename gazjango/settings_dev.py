from settings_base import *

DATABASE_ENGINE   = 'sqlite3'
#For the importer to work, this needs to be an absolute path.
DATABASE_NAME     = BASE + '/development.db'
DATABASE_USER     = ''
DATABASE_PASSWORD = ''
DATABASE_HOST     = ''
DATABASE_PORT     = ''

CACHE_BACKEND = 'locmem:///'

import django
ADMIN_MEDIA_PATH = django.__path__[0] + '/contrib/admin/media/'

LOCAL_JQUERY = True

GMAPS_API_KEY_DAILY = GMAPS_API_KEY
GMAPS_API_KEY_LOCALHOST =  'ABQIAAAAjWbJvs7_o1h7mvy1LX4wLhRi_j0U6kJrkFvY4-OX2XYmEAa76BT975_ke_6OwhnMsE-R1a6oxMkvzw'
GMAPS_API_KEY_127 = 'ABQIAAAA__HcO8eeRwet5zvnoNmWOBRi_j0U6kJrkFvY4-OX2XYmEAa76BR3_-DW8mZq_Cio0OE_2C5MsfnlBg'
GMAPS_API_KEY = GMAPS_API_KEY_LOCALHOST
