from django.core.management.base import NoArgsCommand
from django.core.mail            import EmailMessage, EmailMultiAlternatives, SMTPConnection
from django.http                 import HttpRequest
from gazjango.subscriptions.models import Subscriber
from gazjango.issues.views         import latest_issue
import datetime
import sys
import smtplib

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        dummy_request = HttpRequest()
        dummy_request.GET['for_email'] = 'true'
        html_content = latest_issue(dummy_request).content
        text_content = latest_issue(dummy_request, plain=True).content
        
        dummy_request.GET['racy'] = 'no'
        tame_html_content = latest_issue(dummy_request).content
        tame_text_content = latest_issue(dummy_request, plain=True).content
        
        # Thursday, October 2, 2008; not Thursday, October 02, 2008
        today = datetime.date.today()
        subject = today.strftime("%A, %B !!, %Y").replace("!!", str(today.day))
        
        from_email = "The Daily Gazette <dailygazette@swarthmore.edu>"
        
        print 'starting to send emails, ' + datetime.datetime.now().strftime("%c")
        
        connection = SMTPConnection()
        for subscriber in Subscriber.issues.all():
            if subscriber.plain_text:
                content = text_content if subscriber.racy_content else tame_text_content
                msg = EmailMessage(subject, content, from_email, [subscriber.email])
            else:
                text = text_content if subscriber.racy_content else tame_text_content
                html = html_content if subscriber.racy_content else tame_html_content
                msg = EmailMultiAlternatives(subject, text, from_email, [subscriber.email])
                msg.attach_alternative(html, 'text/html')
            
            try:
                connection.send_messages([msg])
            except smtplib.SMTPRecipientsRefused:
                sys.stderr.write("recipient refused: %s" % subscriber.email)
        
        print 'done sending emails, ' + datetime.datetime.now().strftime("%c")
    
