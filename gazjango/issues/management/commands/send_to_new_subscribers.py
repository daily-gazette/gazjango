from gazjango.issues.management.commands import send_issue_directly
from gazjango.subscriptions.models import Subscriber

class Command(send_issue_directly.Command):
    subscriber_base = Subscriber.issues.filter(last_sent='')
