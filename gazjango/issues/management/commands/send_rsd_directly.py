from django.core.management.base import NoArgsCommand
from django.core.mail            import EmailMessage, EmailMultiAlternatives
from django.http                 import HttpRequest
from gazjango.issues.views  import rsd_now
import datetime

RSD_LIST      = 'reserved-students@sccs.swarthmore.edu'
RSD_TEXT_LIST = 'reserved-text-students@sccs.swarthmore.edu'

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        dummy_request = HttpRequest()
        dummy_request.GET['for_email'] = 'true'
        html_content = rsd_now(dummy_request).content
        text_content = rsd_now(dummy_request, plain=True).content
        
        now = datetime.datetime.now()
        time = 'Morning' if now.hour < 12 else 'Afternoon'
        subject = now.strftime("Reserved Students Digest: @@ of %A, %B !!, %Y")
        subject = subject.replace('@@', time).replace('!!', str(now.day))
        
        from_email = "RSD by the Daily Gazette <dailygazette@swarthmore.edu>"
        
        messages = []
        for subscriber in Subscriber.rsd.all():
            if subscriber.plain_text:
                msg = EmailMessage(subject, text_content, from_email, [subscriber.email])
            else:
                msg = EmailMultiAlternatives(subject, text_content, from_email, [subscriber.email])
                msg.attach_alternative(html_content, 'text/html')
            messages.append(msg)
        
        connection = SMTPConnection()
        connection.send(messages)
    
