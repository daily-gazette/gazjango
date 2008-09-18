from django.conf import settings
import datetime

def is_from_swat(user=None, ip=None):
    if user:
        return user.is_from_swat(ip=ip)
    else:
        return ip_from_swat(ip)

def ip_from_swat(ip):
    return ip and ip.startswith(settings.SWARTHMORE_IP_BLOCK)


# I didn't write this, because I'm lazy and it should be a builtin.
# by Mike C. Fletcher, by way of MonkeeSage
# http://rightfootin.blogspot.com/2006/09/more-on-python-flatten.html
def flatten(l, ltypes=(list, tuple)):
    """
    Takes a nested list and returns it un-nested.
    
    >>> flatten([[1, [2], [3, 4], [[[[5]]]]]])
    [1, 2, 3, 4, 5]
    """
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                if not len(l):
                    break
            else:
                l[i:i+1] = list(l[i])
        i += 1
    return l


def get_static_path(kind, name):
    return "/static/%s/%s" % (kind, name)

def get_jquery_path():
    if settings.LOCAL_JQUERY:
        return get_static_path('js', 'jquery-1.2.6.min.js')
    else:
        return "http://ajax.googleapis.com/ajax/libs/jquery/1.2/jquery.min.js"

