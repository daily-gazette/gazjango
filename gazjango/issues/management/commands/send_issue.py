from django.core.management.base import NoArgsCommand
from django.core.mail            import EmailMessage, EmailMultiAlternatives, SMTPConnection
from django.http                 import HttpRequest
from gazjango.issues.views import latest_issue
import datetime

NORMAL_LIST      = 'gazette-subscribers@sccs.swarthmore.edu'
NORMAL_TEXT_LIST = 'gazette-text-subscribers@sccs.swarthmore.edu'
TAME_LIST        = 'gazette-nonexplicit-subscribers@sccs.swarthmore.edu'
TAME_TEXT_LIST   = 'gazette-nonexplicit-text-subscribers@sccs.swarthmore.edu'

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
        
        html = EmailMultiAlternatives(subject, text_content, from_email, [NORMAL_LIST])
        html.attach_alternative(html_content, 'text/html')
        text = EmailMessage(subject, text_content, from_email, [NORMAL_TEXT_LIST])
        
        tame_html = EmailMultiAlternatives(subject, tame_text_content, from_email, [TAME_LIST])
        tame_html.attach_alternative(tame_html_content, 'text/html')
        tame_text = EmailMessage(subject, text_content, from_email, [TAME_TEXT_LIST])
        
        connection = SMTPConnection()
        connection.send_messages([html, text, tame_html, tame_text])
    
