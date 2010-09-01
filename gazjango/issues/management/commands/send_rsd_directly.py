from gazjango.issues.management.commands import SendingOutCommand
from django.core.management.base         import CommandError
from django.http                         import Http404
from gazjango.issues.views         import show_rsd
from gazjango.subscriptions.models import Subscriber
import datetime

class Command(SendingOutCommand):
    from_email = "Reserved Students Digest <dailygazette@swarthmore.edu>"
    subscriber_base = Subscriber.rsd
    
    def set_content(self, dummy_request):
        try:
            html_response = show_rsd(dummy_request)
            if html_response.status_code == 404:
                raise Http404
        except Http404:
            print "No content, so not sending out."
            raise CommandError('no content')
        
        self.html_content = html_response.content
        self.text_content = show_rsd(dummy_request, plain=True).content
    
    def get_subject(self):
        now = datetime.datetime.now()
        return now.strftime("%%A, %%B %d - Announcements" % now.day)
    
    def get_sent_str(self):
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d-a")
