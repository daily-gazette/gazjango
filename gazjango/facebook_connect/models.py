# FacebookConnectMiddleware.py
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from gazjango.accounts.models import UserProfile
from django.conf import settings
from settings import FACEBOOK_LOGIN_API_KEY, FACEBOOK_LOGIN_SECRET, FACEBOOK_LOGIN_APP_ID, FACEBOOK_UID

import md5
import urllib
import time
import simplejson
from datetime import datetime

# These values could be placed in Django's project settings
API_KEY = FACEBOOK_LOGIN_API_KEY
API_SECRET = FACEBOOK_LOGIN_SECRET

REST_SERVER = 'http://api.facebook.com/restserver.php'

# You can get your User ID here: http://developers.facebook.com/tools.php?api
MY_FACEBOOK_UID = FACEBOOK_UID

PROBLEM_ERROR = 'There was a problem. Try again later.'
ACCOUNT_DISABLED_ERROR = 'Your account is not active.'
ACCOUNT_PROBLEM_ERROR = 'There is a problem with your account.'

class FacebookConnectMiddleware(object):
    
    delete_fb_cookies = False
    facebook_user_is_authenticated = False
    
    def process_request(self, request):
        try:
             # Set the facebook message to empty. This message can be used to dispaly info from the middleware on a Web page.
            request.facebook_message = None

            # Don't bother trying FB Connect login if the user is already logged in
            if not request.user.is_authenticated():
            
                # FB Connect will set a cookie with a key == FB App API Key if the user has been authenticated
                if API_KEY in request.COOKIES:

                    signature_hash = self.get_facebook_signature(request.COOKIES, True)
                
                    # The hash of the values in the cookie to make sure they're not forged
                    if(signature_hash == request.COOKIES[API_KEY]):
                
                        # If session hasn't expired
                        if(datetime.fromtimestamp(float(request.COOKIES[API_KEY+'_expires'])) > datetime.now()):

                                try:
                                    # Try to get Django account corresponding to friend
                                    # Authenticate then login (or display disabled error message)
                                    django_user = User.objects.get(username=request.COOKIES[API_KEY + '_user'])
                                    user = authenticate(username=request.COOKIES[API_KEY + '_user'], 
                                                        password=md5.new(request.COOKIES[API_KEY + '_user'] + settings.SECRET_KEY).hexdigest())
                                    if user is not None:
                                        if user.is_active:
                                            login(request, user)
                                            self.facebook_user_is_authenticated = True
                                        else:
                                            request.facebook_message = ACCOUNT_DISABLED_ERROR
                                            self.delete_fb_cookies = True
                                    else:
                                       request.facebook_message = ACCOUNT_PROBLEM_ERROR
                                       self.delete_fb_cookies = True
                                   except User.DoesNotExist:
                                       # There is no Django account for this Facebook user.
                                       # Create one, then log the user in.

                                       # Make request to FB API to get user's first and last name
                                       user_info_params = {
                                           'method': 'Users.getInfo',
                                           'api_key': API_KEY,
                                           'call_id': time.time(),
                                           'v': '1.0',
                                           'uids': request.COOKIES[API_KEY + '_user'],
                                           'fields': 'first_name,last_name',
                                           'format': 'json',
                                       }
                                       user_info_hash = self.get_facebook_signature(user_info_params)
                                       user_info_params['sig'] = user_info_hash
                                       user_info_params = urllib.urlencode(user_info_params)
                                       user_info_response  = simplejson.load(urllib.urlopen(REST_SERVER, user_info_params))


                                       # Create user
                                       user = User.objects.create_user(request.COOKIES[API_KEY + '_user'], '', 
                                                                       md5.new(request.COOKIES[API_KEY + '_user'] + 
                                                                       settings.SECRET_KEY).hexdigest())
                                       user_profile = user.userprofile_set.create()
                                       user.first_name = user_info_response[0]['first_name']
                                       user.last_name = user_info_response[0]['last_name']
                                       for affiliation in user_info_respeonse[0]['affiliations']:
                                           if affiliation['name'] == 'Swarthmore':
                                               user_profile._from_swat = True
                                       user_profile.save()
                                       user.save()

                                       # Authenticate and log in (or display disabled error message)
                                       user = authenticate(username=request.COOKIES[API_KEY + '_user'], 
                                                           password=md5.new(request.COOKIES[API_KEY + '_user'] + settings.SECRET_KEY).hexdigest())
                                       if user is not None:
                                           if user.is_active:
                                               login(request, user)
                                               self.facebook_user_is_authenticated = True
                                           else:
                                               request.facebook_message = ACCOUNT_DISABLED_ERROR
                                               self.delete_fb_cookies = True
                                       else:
                                          request.facebook_message = ACCOUNT_PROBLEM_ERROR
                                          self.delete_fb_cookies = True
                            
                        # Cookie session expired
                        else:
                            logout(request)
                            self.delete_fb_cookies = True
                        
                   # Cookie values don't match hash
                    else:
                        logout(request)
                        self.delete_fb_cookies = True
                    
            # Logged in
            else:
                # If FB Connect user
                if API_KEY in request.COOKIES:
                    # IP hash cookie set
                    if 'fb_ip' in request.COOKIES:
                        
                        try:
                            real_ip = request.META['HTTP_X_FORWARDED_FOR']
                        except KeyError:
                            real_ip = request.META['REMOTE_ADDR']
                        
                        # If IP hash cookie is NOT correct
                        if request.COOKIES['fb_ip'] != md5.new(real_ip + API_SECRET + settings.SECRET_KEY).hexdigest():
                             logout(request)
                             self.delete_fb_cookies = True
                    # FB Connect user without hash cookie set
                    else:
                        logout(request)
                        self.delete_fb_cookies = True
                        
        # Something else happened. Make sure user doesn't have site access until problem is fixed.
        except:
            request.facebook_message = PROBLEM_ERROR
            logout(request)
            self.delete_fb_cookies = True
        
    def process_response(self, request, response):        
        
        # Delete FB Connect cookies
        # FB Connect JavaScript may add them back, but this will ensure they're deleted if they should be
        if self.delete_fb_cookies is True:
            response.delete_cookie(API_KEY + '_user')
            response.delete_cookie(API_KEY + '_session_key')
            response.delete_cookie(API_KEY + '_expires')
            response.delete_cookie(API_KEY + '_ss')
            response.delete_cookie(API_KEY)
            response.delete_cookie('fbsetting_' + API_KEY)
    
        self.delete_fb_cookies = False
        
        if self.facebook_user_is_authenticated is True:
            try:
                real_ip = request.META['HTTP_X_FORWARDED_FOR']
            except KeyError:
                real_ip = request.META['REMOTE_ADDR']
            response.set_cookie('fb_ip', md5.new(real_ip + API_SECRET + settings.SECRET_KEY).hexdigest())
        
        # process_response() must always return a HttpResponse
        return response
                                
    # Generates signatures for FB requests/cookies
    def get_facebook_signature(self, values_dict, is_cookie_check=False):
        signature_keys = []
        for key in sorted(values_dict.keys()):
            if (is_cookie_check and key.startswith(API_KEY + '_')):
                signature_keys.append(key)
            elif (is_cookie_check is False):
                signature_keys.append(key)

        if (is_cookie_check):
            signature_string = ''.join(['%s=%s' % (x.replace(API_KEY + '_',''), values_dict[x]) for x in signature_keys])
        else:
            signature_string = ''.join(['%s=%s' % (x, values_dict[x]) for x in signature_keys])
        signature_string = signature_string + API_SECRET

        return md5.new(signature_string).hexdigest()