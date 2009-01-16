from django.conf import settings

def api_keys(request):
    return { 'FACEBOOK_API_KEY': settings.FACEBOOK_LOGIN_API_KEY }

def login_status(request):
    return { 'facebook_user': request.facebook_user,
             'facebook_message': request.facebook_message }
