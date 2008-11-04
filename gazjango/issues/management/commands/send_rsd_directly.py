from django.core.management.base import NoArgsCommand
from django.core.mail            import EmailMessage, EmailMultiAlternatives, SMTPConnection
from django.http                 import HttpRequest
from gazjango.subscriptions.models import Subscriber
from gazjango.issues.views         import rsd_now
import datetime
import sys
import smtplib

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        dummy_request = HttpRequest()
        dummy_request.GET['for_email'] = 'true'
        html_content = rsd_now(dummy_request).content
        text_content = rsd_now(dummy_request, plain=True).content
        
        now = datetime.datetime.now()
        time = 'Morning' if now.hour < 12 else 'Afternoon'
        subject = now.strftime("@@ of %A, %B !!, %Y")
        subject = subject.replace('@@', time).replace('!!', str(now.day))
        
        from_email = "RSD by the Daily Gazette <dailygazette@swarthmore.edu>"
        
        print 'starting to send emails, ' + datetime.datetime.now().strftime("%c")
        
        connection = SMTPConnection()
        to_send = [(subscriber, 0) for subscriber in Subscriber.rsd.all()]
        while to_send:
            subscriber, count = to_send.pop(0)
            if count > 5:
                sys.stderr.write('giving up on %s\n' % subscriber.email)
                continue
            
            if subscriber.plain_text:
                msg = EmailMessage(subject, text_content, from_email, [subscriber.email])
            else:
                msg = EmailMultiAlternatives(subject, text_content, from_email, [subscriber.email])
                msg.attach_alternative(html_content, 'text/html')
            
            try:
                connection.send_messages([msg])
            except smtplib.SMTPRecipientsRefused:
                sys.stderr.write("recipient refused: %s" % subscriber.email)
            except Exception, e:
                sys.stderr.write("%s: error sending to %s\n%s: %s\n%s\n\n" % 
                        (datetime.datetime.now().strftime("%c"),
                         subscriber,
                         e.__class__.__name__,
                         e.message,
                         traceback.format_exc()))
                to_send.append((subscriber, count + 1))
        
        print 'done sending emails, ' + datetime.datetime.now().strftime("%c")
