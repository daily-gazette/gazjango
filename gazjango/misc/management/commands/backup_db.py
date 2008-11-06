from django.core.management.base import NoArgsCommand, CommandError
from django.conf import settings
import datetime
import sys, os, os.path

DUMP_PATTERN = "/home/dailygazette/db-backups/dump_%Y-%m-%d_%H-%M.sql"

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        if settings.DATABASE_ENGINE != 'mysql':
            raise CommandError("This command requires a mysql database.")
        
        args = []
        if settings.DATABASE_HOST:
            args.append('--host=%s' % settings.DATABASE_HOST)
        if settings.DATABASE_PORT:
            args.append('--port=%s' % settings.DATABASE_PORT)
        if settings.DATABASE_USER:
            args.append('--user=%s' % settings.DATABASE_USER)
        if settings.DATABASE_PASSWORD:
            args.append('--password=%s' % settings.DATABASE_PASSWORD)
        args.append(settings.DATABASE_NAME)
        
        filename = datetime.datetime.now().strftime(DUMP_PATTERN)
        backup_dir = os.path.dirname(filename)
        if not os.path.exists(backup_dir):
            os.path.makedirs(backup_dir)
        
        print "Backing up %s to %s" % (args[-1], filename)
        os.system('mysqldump %s | bzip2 > %s' % (' '.join(args), filename))
    
