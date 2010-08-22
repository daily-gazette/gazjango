This is the source for the [Daily Gazette](http://daily.swarthmore.edu)'s website.

If you don't work for the Gazette, you're welcome to check out the code (obviously), but you won't have access to the database files and whatnot.

Getting started:

 * Make sure you have Python (2.5, 2.6, or 2.7), Django, MySQL, and MySQLdb installed
 * Clone the repository
 * Get `settings_secret.py` from `sccs.swarthmore.edu:~aquinton/settings_secret.py` (this has API keys and such)
 * Set up a MySQL database for the project
 * Create a `settings.py` file with at least these contents:

    from settings_dev import *

    DATABASE_ENGINE = 'mysql'
	DATABASE_NAME = 'gazette' # or whatever you set up the db name to be
	DATABASE_USER = 'your_mysql_username'
	DATABASE_PASSWORD = 'your_mysql_password'
	DATABASE_HOST = 'localhost'
	DATABASE_PORT = ''

 * Get a DB backup from `sccs.swarthmore.edu:~aquinton/db_backups`. It'll be something like `gazjango_2010-08-22_07-00.sql.bz2`.
 * Put the DB file into your local repository: `bzcat gazjango_2010-08-22_07-00.sql.bz2 | ./manage.py dbshell`
 * Update stuff for the community feed: `bash ./update.sh`
