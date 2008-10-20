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
     * rsd
     * rsd-text
    """
    def handle(self, *args, **kwargs):
        filters = {
            'normal':    Q(receive='i', plain_text=False, racy_content=True),
            'text':      Q(receive='i', plain_text=True,  racy_content=True),
            'tame':      Q(receive='i', plain_text=False, racy_content=False),
            'tame-text': Q(receive='i', plain_text=True,  racy_content=False),
            'rsd':       Q(receive='r', plain_text=False),
            'rsd-text':  Q(receive='r', plain_text=True),
        }
        if not args or len(args) != 1 or args[0] not in filters.keys():
            raise CommandError('Enter exactly one subscriber category.')
        
        # can't do this directly, because some are keyed to users :/
        subscribers = Subscriber.active.filter(filters[args[0]])
        return '\n'.join(sub.email for sub in subscribers)
    
