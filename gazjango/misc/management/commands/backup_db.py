from django.core.management.base import NoArgsCommand, CommandError
from django.conf import settings
from subprocess import Popen
import datetime
import sys

DUMP_PATTERN = "/home/dailygazette/db-backups/dump_%Y-%m-%d_%H-%M.sql.bz2"

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        if settings.DATABASE_ENGINE != 'mysql':
            raise CommandError("This command requires a mysql database.")
        args = {
            'host': settings.DATABASE_HOST,
            'port': settings.DATABASE_PORT,
            'name': settings.DATABASE_NAME,
            'user': settings.DATABASE_USER,
            'pwd' : settings.DATABASE_PASSWORD,
        }
        
        cmd = "mysqldump --host='%(host)s' --port='%(port)s' --user='%(user)s' " + \
              "--password='%(pwd)s' %(name)s"
        filename = datetime.datetime.now().strftime(DUMP_PATTERN)
        process = Popen(cmd % args,
                        stdout=open(filename, 'w'),
                        stderr=open(filename + '.errors', 'w'))
        process.wait()
    
