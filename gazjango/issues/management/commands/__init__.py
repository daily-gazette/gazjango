from django.core.management.base import NoArgsCommand
from django.core.mail            import EmailMessage, SMTPConnection, mail_admins
from django.http                 import HttpRequest
import datetime
import time
import sys
import smtplib
import traceback
import pickle

class SendingOutCommand(NoArgsCommand):
    subscriber_base = None # Subscriber.rsd or whatever
    from_email = 'The Daily Gazette <dailygazette@swarthmore.edu>'
    WAIT_TIME = 60
    
    def set_content(self, dummy_request):
        raise NotImplemented
    
    def get_subject(self):
        today = datetime.date.today()
        return today.strftime("%%A, %%B %d, %%Y" % today.day)
    
    def get_sent_str(self):
        return datetime.date.today().strftime('%Y-%m-%d')
    
    def contents_for_subscriber(self, subscriber):
        return (self.text_content, self.html_content)
    
    
    def send_to_subscriber(self, subscriber):
        text_content, html_content = self.contents_for_subscriber(subscriber)
        
        msg = EmailMessage(self.subject, text_content, self.from_email, [subscriber.email])
        if not subscriber.plain_text:
            msg.multipart_subtype = 'alternative'
            msg.attach(content=html_content, mimetype='text/html')
        
        self.connection.send_messages([msg])
        
        # if it didn't just crash, sending was successful :)
        subscriber.last_sent = self.sent_str
        subscriber.save()
    
    def try_sending_to_subscriber(self, subscriber, repeat_index=0, max_repeats=2):
        if repeat_index >= max_repeats:
            return
        
        try:
            self.send_to_subscriber(subscriber)
        except smtplib.SMTPRecipientsRefused:
            self.add_error(subscriber, 'recipient refused')
        except smtplib.SMTPServerDisconnected:
            self.add_error(subscriber, 'server disconnected')
            self.connection.open()
            self.try_sending_to_subscriber(subscriber, repeat_index + 1, max_repeats)
        except smtplib.SMTPException:
            self.add_error(subscriber, 'smtp error')
        except Exception:
            self.add_error(subscriber, 'generic error')
    
    def add_error(self, subscriber, key):
        self.errors.setdefault(subscriber, {})
        self.errors[subscriber].setdefault(key, [])
        exc_type, exc_val, exc_trace = sys.exc_info()
        self.errors[subscriber][key].append({
            'type': exc_type,
            'val': exc_val,
            'traceback': ''.join(traceback.format_exception(exc_type, exc_val, exc_trace)),
            'time': datetime.datetime.now()
        })
    
    
    def handle_noargs(self, **options):
        dummy_request = HttpRequest()
        dummy_request.GET['for_email'] = 'true'
        self.set_content(dummy_request)
        
        self.subject = self.get_subject()
        self.sent_str = self.get_sent_str()
        
        self.connection = SMTPConnection()
        self.errors = {}
        
        print 'starting: ' + datetime.datetime.now().strftime("%c")
        
        # try up to four times, if necessary
        for i in range(4):
            not_sent = self.subscriber_base.exclude(last_sent=self.sent_str)
            if len(not_sent): # intentionally resolve the query
                if i != 0:
                    print datetime.datetime.now().strftime('%c'), 
                    print '- sleeping before retrying %s emails...' % len(not_sent)
                    time.sleep(self.WAIT_TIME)
                for subscriber in not_sent:
                    self.try_sending_to_subscriber(subscriber)
        
        # any that *still* didn't work?
        error_output = []
        for sub in self.subscriber_base.exclude(last_sent=self.sent_str):
            errors = [ '%d %s' % (len(data), kind) for kind, data 
                       in self.errors[sub].items() ]
            error_output.append('errors with %s: %s' % (sub.email, '\t'.join(errors)))
        
        if error_output:
            print '\n', '\n'.join(error_output), '\n'
            mail_admins('Errors sending out',
                "Got the following errors while sending the email:\n" +
                '\n'.join(error_output) +
                '\n\nMore information is available by loading the pickled log file.'
            )
        
        if self.errors:
            print 'more info available in the pickle file'
        pickle.dump(self.errors, sys.stderr)
        
        print 'finished: ' + datetime.datetime.now().strftime("%c")
