from django.core.management.base import NoArgsCommand
from django.core.mail            import EmailMessage, EmailMultiAlternatives
from django.http                 import HttpRequest
from gazjango.issues.views  import rsd_now
import datetime

RSD_LIST = 'reserved-students@sccs.swarthmore.edu'
# FIXME: this address doesn't actually exist :)
RSD_TEXT_LIST = 'reserved-students-text@sccs.swarthmore.edu'

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        dummy_request = HttpRequest()
        html_content = rsd_now(dummy_request).content
        text_content = rsd_now(dummy_request, plain=True).content
        
        now = datetime.datetime.now()
        time = 'Morning' if now.hour < 12 else 'Afternoon'
        subject = now.strftime("Reserved Students Digest: @@ of %A, %B !!, %Y")
        subject = subject.replace('@@', time).replace('!!', str(today.day))
        
        from_email = "RSD by the Daily Gazette <dailygazette@swarthmore.edu>"
        
        email = EmailMultiAlternatives(subject, text_content, from_email, [RSD_LIST])
        email.attach_alternative(html_content, 'text/html')
        email.send()
        
        text = EmailMessage(subject, text_content, from_email, [RSD_TEXT_LIST])
        text.send()
    
