This is the source for the [Daily Gazette](http://daily.swarthmore.edu)'s website.

Here's how you can set it up for dev access.

If you don't work for the Gazette, you're welcome to check out the code (obviously), but you won't have access to the database files and whatnot.

Make sure you have Python (2.5, 2.6, or 2.7), Django, MySQL, and MySQLdb installed

Clone the repository. The commands below assume you're in the `gazjango` directory (ie the one with `manage.py`).

Get `settings_secret.py` from `sccs.swarthmore.edu:~aquinton/settings_secret.py` (this has API keys and such).

Set up a MySQL database for the project (`mysqladmin -u root create gazette`).

Create a `settings.py` file with at least these contents:
    from settings_dev import *

    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.mysql',
            'NAME':     'gazette',
            'USER':     'root',
            'PASSWORD': '',
        }
    }


Get a DB backup from `sccs.swarthmore.edu:~aquinton/db_backups`. It'll be something like `gazjango_2010-08-22_07-00.sql.bz2`.

Put the DB file into your local repository: `bzcat gazjango_2010-08-22_07-00.sql.bz2 | ./manage.py dbshell`

(This should go away shortly, but run `bash ../migration.sh` to convert from the old DB format, which the website is running, to the new one.)

Get all of the uploaded media files off the website: `./sync_uploads.sh`

Update stuff for the community feed: `python ./update.py`

Compile the CSS templates into real stylesheets: `./compile_css`

Now you should be able to do `./manage.py runserver`, `./manage.py shell`, etc.
