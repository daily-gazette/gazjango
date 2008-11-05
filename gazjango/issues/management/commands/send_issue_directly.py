from django.core.management.base import NoArgsCommand
from django.core                 import mail
from django.http                 import HttpRequest
from gazjango.subscriptions.models import Subscriber
from gazjango.issues.views         import latest_issue
import datetime
import traceback
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
        
        if not (200 <= html_content.status_code < 300):
            mail.mail_admins('OH NO: %s IN SENDING THE ISSUE' % html_content.status_code,
                             'Check /issue and ~/issue_output. Sent it anyway.')
        
        # Thursday, October 2, 2008; not Thursday, October 02, 2008
        today = datetime.date.today()
        subject = today.strftime("%A, %B !!, %Y").replace("!!", str(today.day))
        
        from_email = "The Daily Gazette <dailygazette@swarthmore.edu>"
        
        print 'starting to send emails, ' + datetime.datetime.now().strftime("%c")
        
        connection = mail.SMTPConnection()
        to_send = [(subscriber, 0) for subscriber in Subscriber.issues.all()]
        
        while to_send:
            subscriber, count = to_send.pop(0)
            if count > 5:
                sys.stderr.write('giving up on %s\n' % subscriber)
                continue
                
            if subscriber.plain_text:
                content = text_content if subscriber.racy_content else tame_text_content
                msg = mail.EmailMessage(subject, content, from_email, [subscriber.email])
            else:
                text = text_content if subscriber.racy_content else tame_text_content
                html = html_content if subscriber.racy_content else tame_html_content
                msg = mail.EmailMultiAlternatives(subject, text, from_email, [subscriber.email])
                msg.attach_alternative(html, 'text/html')
            
            try:
                connection.send_messages([msg])
            except smtplib.SMTPRecipientsRefused:
                sys.stderr.write("recipient refused: %s\n" % subscriber.email)
            except Exception, e:
                sys.stderr.write("%s: error sending to %s\n%s: %s\n%s\n\n" % 
                        (datetime.datetime.now().strftime("%c"),
                         subscriber,
                         e.__class__.__name__,
                         e.message,
                         traceback.format_exc()))
                to_send.append((subscriber, count + 1))
        
        print 'done sending emails, ' + datetime.datetime.now().strftime("%c")
    
