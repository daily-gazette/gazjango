from django.core.management.base                 import NoArgsCommand
from gazjango.misc.management.commands.backup_db import DUMP_DIRECTORY, DUMP_PATTERN
import os, re

DUMP_MATCHER = re.compile(r"^%s$" % re.sub(r'%[a-zA-Z]',
                                           r'.+', 
                                           re.escape(DUMP_PATTERN)))
NUM_TO_SAVE = 8

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        dumps = [f for f in os.listdir(DUMP_DIRECTORY) if DUMP_MATCHER.match(f)]
        dumps.sort(reverse=True)
        
        for f in dumps[NUM_TO_SAVE:]:
            print "removing %s" % f
            os.remove(os.path.join(DUMP_DIRECTORY, f))
    
