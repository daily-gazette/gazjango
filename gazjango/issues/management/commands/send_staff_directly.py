from gazjango.issues.management.commands import SendingOutCommand
from django.core.management.base         import CommandError
from django.core.mail                    import mail_admins
from django.http                         import Http404

from gazjango.articles.views       import Issue
from gazjango.options.helpers      import is_publishing
from gazjango.subscriptions.models import Subscriber

import datetime

class Command(SendingOutCommand):
    from_email = "The Gazette <editor@daily.swarthmore.edu>"
    subscriber_base = Subscriber.staff
    
    def set_content(self, dummy_request):
        try:
            html_response = staff_mail(dummy_request)
            if html_response.status_code == 404:
                raise Http404
        except Http404:
            print "No content, so not sending out."
            raise CommandError('no content')
        
        self.html_content = html_response.content
    
    def get_subject(self):
        now = datetime.datetime.now()
        name = "Gazette Minutes"
        return now.strftime("%s of %%A, %%B %d, %%Y" % (name, now.day))
    
    def get_sent_str(self):
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d-" + ("1" if now.hour < 12 else "2"))
