# based on  http://nyquistrate.com/django/facebook-connect/
from django.conf                import settings
from django.contrib.auth        import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils               import simplejson

from gazjango.accounts.models   import UserProfile, UserKind
from gazjango.misc.helpers      import find_unique_name
from gazjango.misc.view_helpers import get_ip, get_user_profile

import md5
import urllib, urllib2
import time
import datetime

API_KEY = settings.FACEBOOK_LOGIN_API_KEY
API_SECRET = settings.FACEBOOK_LOGIN_SECRET
REST_SERVER = 'http://api.facebook.com/restserver.php'

PROBLEM_ERROR = 'There was a problem. Try again later.'
ACCOUNT_DISABLED_ERROR = 'Your account is not active.'
ACCOUNT_PROBLEM_ERROR = 'There is a problem with your account.'

class FacebookConnectMiddleware(object):
    delete_fb_cookies = False
    facebook_user_is_authenticated = False
    
    def username(self, request):
        return 'facebook-' + self.cookie(request, '_user')
    
    def logout(self, request):
        logout(request)
        request.facebook_user = None
        self.delete_fb_cookies = True
        return None
    
    def hash(self, thing):
        return md5.new(thing + settings.SECRET_KEY).hexdigest()
    
    def cookie(self, request, key):
        return request.COOKIES[API_KEY + key]
    
    # Generates signatures for FB requests/cookies
    def get_facebook_signature(self, values_dict, is_cookie_check=False):
        signature_keys = []
        for key in sorted(values_dict.keys()):
            if is_cookie_check and key.startswith(API_KEY + '_'):
                signature_keys.append(key)
            elif is_cookie_check is False:
                signature_keys.append(key)
        
        if is_cookie_check:
            signature_string = ''.join('%s=%s' % (x.replace(API_KEY + '_',''), values_dict[x])
                                       for x in signature_keys)
        else:
            signature_string = ''.join('%s=%s' % (x, values_dict[x]) for x in signature_keys)
        
        return md5.new(signature_string + API_SECRET).hexdigest()
    
    def verify_facebook_cookies(self, request):
        # check the hash of the cookie values, to prevent forgery
        signature_hash = self.get_facebook_signature(request.COOKIES, True)
        if signature_hash != request.COOKIES[API_KEY]:
            return False
        
        # check expiry
        expiry = float(self.cookie(request, '_expires'))
        if (datetime.datetime.fromtimestamp(expiry) <= datetime.datetime.now()):
            return False
        
        return True
    
    
    def create_user(self, request):
        user_info_params = {
            'method': 'Users.getInfo',
            'api_key': API_KEY,
            'call_id': time.time(),
            'v': '1.0',
            'uids': self.cookie(request, '_user'),
            'fields': 'first_name,last_name,affiliations',
            'format': 'json',
        }
        user_info_params['sig'] = self.get_facebook_signature(user_info_params)
        user_info_params = urllib.urlencode(user_info_params)
        user_info_r = simplejson.load(urllib2.urlopen(REST_SERVER, user_info_params))
        user_info = user_info_r[0]
        
        user = User.objects.create_user(
            find_unique_name(
                "%s_%s" % (user_info['first_name'], user_info['last_name']),
                User.objects, 'username', '_'),
            ''
        )
        user_profile = user.userprofile_set.create()
        
        user.first_name = user_info['first_name']
        user.last_name = user_info['last_name']
        user.facebook_id = self.cookie(request, '_user')                              
        
        if user_info['affiliations']:
            for affiliation in user_info['affiliations']:
                if affiliation['name'] == 'Swarthmore':
                    user_profile.from_swat = True
                    user_profile.kind, created = UserKind.objects.get_or_create(
                        kind='s' if affiliation['status'] == 'Undergrad' else 'a',
                        year=affiliation['year']
                    )
        
        user.save()
        user_profile.save()
        return user, user_profile
    
    
    def process_request(self, request):
        try:
            # Set the facebook message to empty. This message can be used to
            # display info from the middleware on a Web page.
            request.facebook_message = None
            request.facebook_user = None
            
            if request.user.is_authenticated():
                if API_KEY in request.COOKIES: # using FB Connect
                    if 'fb_ip' not in request.COOKIES: # we haven't been associated yet
                        if not self.verify_facebook_cookies(request):
                            return self.logout(request)
                        profile = get_user_profile(request)
                        if profile.facebook_id:
                            # already associated with a facebook account: oh well,
                            # let's just change it.
                            pass
                        profile.facebook_id = self.cookie(request, '_user')
                        profile.save()
                        self.facebook_user_is_authenticated = True
                        request.facebook_user = request.user
                    
                    elif request.COOKIES['fb_ip'] == self.hash(get_ip(request) + API_SECRET):
                        # all seems to be in order
                        self.facebook_user_is_authenticated = True
                        request.facebook_user = request.user
                    
                    else: # invalid ip! either some proxy stuff or a haxor
                        return self.logout(request)
                
                else: # not using FB Connect
                    pass
            
            else: # not logged in
                if API_KEY in request.COOKIES: # using FB Connect
                    if not self.verify_facebook_cookies(request):
                        return self.logout(request)
                    
                    try:
                        fid = self.cookie(request, '_user')
                        profile = UserProfile.objects.get(facebook_id=fid)
                        user = profile.user
                    except UserProfile.DoesNotExist:
                        user, profile = self.create_user(request)
                    
                    if user is None:
                        request.facebook_message = ACCOUNT_PROBLEM_ERROR
                        self.delete_fb_cookies = True
                    else:
                        if user.is_active:
                            login(request, user)
                            self.facebook_user_is_authenticated = True
                            request.facebook_user = user
                        else:
                            request.facebook_message = ACCOUNT_DISABLED_ERROR
                            self.delete_fb_cookies = True
        
        # something went wrong. make sure user doesn't have site access until problem is fixed.
        except:
            request.facebook_message = PROBLEM_ERROR
            self.logout(request)
    
    def process_response(self, request, response):
        # delete FB Connect cookies -- the js might add them again, but
        # we want them gone if not
        if self.delete_fb_cookies is True:
            response.delete_cookie(API_KEY + '_user')
            response.delete_cookie(API_KEY + '_session_key')
            response.delete_cookie(API_KEY + '_expires')
            response.delete_cookie(API_KEY + '_ss')
            response.delete_cookie(API_KEY)
            response.delete_cookie('fbsetting_' + API_KEY)
        
        self.delete_fb_cookies = False
        
        if self.facebook_user_is_authenticated is True:
            response.set_cookie('fb_ip', self.hash(get_ip(request) + API_SECRET))
        
        return response
    
