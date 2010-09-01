from __future__ import division

from django.conf import settings
from django.core.cache import cache as _djcache
from django.db.models import signals
from django.template.defaultfilters import slugify

import datetime
import re
from hashlib import sha1

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

def groupby(fun, gen):
    '''Inputs: a function and an iterable
    Returns: a dictionary grouping elements by their image under fun
    Exceptional cases: throws TypeError if fun returns something unhashable

    >>> groupby(lambda n: n % 3, range(11))
    {0: [0, 3, 6, 9],  1: [1, 4, 7, 10],  2: [2, 5, 8]}
    '''
    d = {}
    for el in gen:
        val = fun(el)
        if val not in d:
            d[val] = []
        d[val].append(el)
    return d


def get_static_path(kind, name):
    return "/static/%s/%s" % (kind, name)

def get_jquery_path():
    if settings.LOCAL_JQUERY:
        return get_static_path('js', 'jquery-1.4.2.min.js')
    else:
        return "http://ajax.googleapis.com/ajax/libs/jquery/1.4/jquery.min.js"


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


WORD_BREAKS = re.compile(r'[-.,_\s]+')
def smart_truncate(string, length, min_length_diff=15):
    """
    Truncates `string` to be no longer than `length`, but no shorter than
    `length`-`min_length_diff`. Tries to do so at a word boundary, cutting
    off terminal punctuation.
    
    >>> test = lambda *args: (lambda k: (k, len(k)))(smart_truncate(*args))
    >>> test("this is some text", 17)
    ('this is some text', 17)
    >>> test("this is some text", 15)
    ('this is some...', 15)
    >>> test("this is some text", 14)
    ('this is...', 10)
    >>> test("this is some text", 14, 3) # don't let it cut more than 3 chars
    ('this is som...', 14)
    >>> test("this is some, comma splicing", 17)
    ('this is some...', 15)
    >>> test("this is some, comma splicing", 15)
    ('this is some...', 15)
    """
    if len(string) <= length or string.endswith('...'):
        return string
    
    # we'll need to add a '...', so we're effectively trimming it 3 shorter
    length -= 3
    
    # find the rightmost end-of-word
    rev = ''.join(reversed(string[:length+1]))
    match = WORD_BREAKS.search(rev, endpos=min_length_diff)
    if match:
        i = match.end()
        if i <= min_length_diff: # we're trimming an acceptable amount
            return string[:(length+1-i)] + '...'
    return string[:length] + '...'


def cache(seconds=900):
    """
    Caches the results of a function call for the specified number of seconds,
    using the standard Django cache. Assumes it is a pure function (ie only
    depends on its arguments); note also that the exact argument string matters.
    Also note that a result of None will not be cached.
    """
    def doCache(f):
        def x(*args, **kwargs):
            key = sha1(str(f.__module__) + str(f.__name__) + str(args) + str(kwargs)).hexdigest()
            result = _djcache.get(key)
            if result is None:
                result = f(*args, **kwargs)
                _djcache.set(key, result, seconds)
            return result
        return x
    return doCache
