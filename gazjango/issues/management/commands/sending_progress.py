from django.core.management.base import LabelCommand
from gazjango.subscriptions.models import Subscriber
from gazjango.issues.management.commands import send_issue_directly, send_rsd_directly

class Command(LabelCommand):
    def handle_label(self, label, **options):
        if label.startswith('r'):
            base = Subscriber.rsd
            name = 'RSD'
            sent_str = send_rsd_directly.Command().get_sent_str()
        else:
            base = Subscriber.issues
            name = 'issue'
            sent_str = send_issue_directly.Command().get_sent_str()
        
        done = base.filter( last_sent=sent_str).count()
        left = base.exclude(last_sent=sent_str).count()
        print "%s subscribers for %s: %d done, %d to go" % (name, sent_str, done, left)
    
