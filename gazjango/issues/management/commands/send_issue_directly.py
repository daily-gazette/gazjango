from gazjango.issues.management.commands import SendingOutCommand
from django.core.management.base         import CommandError
from django.core.mail                    import mail_admins
from django.http                         import Http404

from gazjango.subscriptions.models import Subscriber
from gazjango.issues.views         import latest_issue

import datetime

class Command(SendingOutCommand):
    subscriber_base = Subscriber.issues
    
    def set_content(self, dummy_request):
        try:
            html_response = latest_issue(dummy_request)
            if html_response.status_code == 404:
                raise Http404
        except Http404:
            mail_admins('ERROR IN SENDING GAZETTE ISSUE FOR '+
                        datetime.date.today().strftime('%A, %B %d, %Y'),
                        "so it didn't get sent. probably no articles.")
            raise CommandError('No issue, so not sending it.')
        
        self.html_content = html_response.content
        self.text_content = latest_issue(dummy_request, plain=True).content
        
        dummy_request.GET['racy'] = 'no'
        self.tame_html_content = latest_issue(dummy_request).content
        self.tame_text_content = latest_issue(dummy_request, plain=True).content
    
    def contents_for_subscriber(self, subscriber):
        if subscriber.racy_content:
            return (self.text_content, self.html_content)
        else:
            return (self.tame_text_content, self.tame_html_content)
    
