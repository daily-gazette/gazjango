from django import template
from django.core.urlresolvers import reverse
from django.utils.safestring  import mark_safe
from django.utils.html        import conditional_escape

from django.contrib.humanize.templatetags.humanize import ordinal

from datetime import date

register = template.Library()

@register.filter
def join_authors(authors, format='', autoescape=None):
    """
    Takes an m2m manager for authors (ie story.authors) and returns a string
    formatted for bylines: something like "JOE SCHMOE, STAFF REPORTER; JANE 
    MCBANE, ARTS EDITOR".
    
    The format argument tells the filter how to format the return value
    (surprisingly enough). This is a string, which can specify as many of the
    following arguments as you want, in whatever order. If you supply
    conflicting format args (and really, why would you?), the last one wins.
    
    If the format string includes an integer, we return only that many authors;
    an "a" returns them all, which is the default.
    
    If the format string includes an "l", we link to authors' profile pages;
    if it includes a "p", for "plain", we do not. Not linking is the default.
    
    If the format string includes a "u", the whole string is upper-case; a
    "d" means the whole string is downcased; a "t" means the string is in
    title-case (like "Joe Schmoe, Staff Reporter"). "u" is default.
    
    If the format string includes an "s", positions are shown; if it includes
    an "x", positions are not shown. "s" is default.
    """
    limit = None
    link = False
    case = 'u'
    positions = True
    for char in format.lower():
        if char.isdigit():
            limit = int(char)
        elif char == 'a':
            limit = None
        elif char in ('l', 'p'):
            link = (char == 'l')
        elif char in ('d', 't', 'u'):
            case = char
        elif char in ('s', 'x'):
            positions = (char == 's')
        else:
            pass
    
    result = list(authors.all()[:limit] if limit else authors.all())
    
    esc = conditional_escape if autoescape else (lambda x: x)
    
    if case == 'd':
        casify = lambda s: esc(s).lower()
    elif case == 'u':
        casify = lambda s: esc(s).upper()
    else: # case == 't'
        casify = lambda s: ' '.join(x.capitalize() for x in esc(s).split())
    
    def reps(author):
        return {
            'url': author.get_absolute_url(),
            'name': casify(author.name),
            'pos': casify(author.position().name) 
        }
    
    base = "%(name)s"
    if positions: base += ", %(pos)s"
    if link: base = "<a href='%(url)s'>" + base + "</a>"
    
    return mark_safe('; '.join([base % reps(author) for author in result]))

join_authors.needs_autoescape = True


@register.filter
def issue_url(date):
    "Returns the url for ``date``'s issue."
    d = { 'year': date.year, 'month': date.month, 'day': date.day }
    return reverse('issue', kwargs=d)

issue_url.is_safe = True


@register.filter
def near_future_date(date):
    """
    Returns just the name of the day if it's in the next few days; if it's
    in the next month, a string like "Tuesday the 5th"; otherwise, a string
    like "May 12".
    """
    distance = (date - date.today()).days
    if 0 < distance < 6:
        return date.strftime("%A")
    elif 0 < distance < 20:
        return date.strftime("%A the ") + ordinal(date.day)
    else:
        return date.strftime("%B ") + str(date.day)

near_future_date.is_safe = True
