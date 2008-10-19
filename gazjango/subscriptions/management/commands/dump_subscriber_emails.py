from django.db.models import Q
from django.core.management.base import BaseCommand, CommandError
from gazjango.subscriptions.models import Subscriber

class Command(BaseCommand):
    """
    Print out the emails of subscribers for the passed category, which should
    be one of the following:
     * normal
     * text
     * tame
     * tame-text
    """
    def handle(self, *args, **kwargs):
        filters = {
            'normal':    Q(plain_text=False, racy_content=True),
            'text':      Q(plain_text=True,  racy_content=True),
            'tame':      Q(plain_text=False, racy_content=False),
            'tame-text': Q(plain_text=True,  racy_content=False),
        }
        if not args or len(args) != 1 or args[0] not in filters.keys():
            raise CommandError('Enter exactly one subscriber category.')
        
        # can't do this directly, because some are keyed to users :/
        subscribers = Subscriber.active.filter(filters[args[0]])
        return '\n'.join(sub.email for sub in subscribers)
    
