from __future__ import division
from django.conf import settings
from django.db.models import signals
from django.template.defaultfilters import slugify
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


def avg(iterable):
    "Returns the average of an iterable of numerics, or None if not defined."
    _c = sum((complex(val, 1) for val in iterable), complex(0,0))
    total = _c.real; count = _c.imag
    return total / count if count > 0 else None


def get_static_path(kind, name):
    return "/static/%s/%s" % (kind, name)

def get_jquery_path():
    if settings.LOCAL_JQUERY:
        return get_static_path('js', 'jquery-1.2.6.min.js')
    else:
        return "http://ajax.googleapis.com/ajax/libs/jquery/1.2/jquery.min.js"


def find_unique_name(basename, qset, fieldname='slug', mixer="-"):
    val = basename
    num = 0
    existing = qset.filter(**{("%s__contains" % fieldname): basename}) \
                   .values_list(fieldname, flat=True)
    while val in existing:
        num += 1
        val = "%s%s%s" % (basename, mixer, num)
    return val


def set_default_slug(namer, extra_limits=lambda x: {}):
    """
    Returns a function to automatically set a default slug after creation.
    
    The base field is defined by the function ``namer``:
        lambda instance: instance.name
    
    If slugs only need to be unique per-year, or some other limitation like
    this, then the function ``extra_limits`` can set that -- for example:
        lambda x: { 'pub_date__year': x.pub_date.year }
    """
    def _func(sender, instance, **kwords):
        if not instance.slug:
            instance.slug = find_unique_name(
                basename=slugify(namer(instance)),
                qset=sender._default_manager.filter(**extra_limits(instance)),
                fieldname='slug',
                mixer='-'
            )
    
    return _func
