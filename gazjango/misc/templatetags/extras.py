from django import template
from django.core.urlresolvers import reverse
from django.utils.safestring  import mark_safe
from django.utils.html        import conditional_escape

from django.contrib.humanize.templatetags.humanize import ordinal

from datetime import date

register = template.Library()


### various filters to ease the outputting of more human text


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
    if 0 <= distance < 6:
        return date.strftime("%A")
    elif 0 < distance < 20:
        return date.strftime("%A the ") + ordinal(date.day)
    else:
        return date.strftime("%B ") + str(date.day)

near_future_date.is_safe = True





### stuff related to the AddThis button


ADD_THIS_PRE = """
<script type="text/javascript">
addthis_pub  = 'dailygazette';
addthis_options = 'facebook, favorites, delicious, twitter, google, live, furl, more';
</script>"""

ADD_THIS_HOVER = """
<a href="http://www.addthis.com/bookmark.php" onmouseover="return addthis_open(this, '', '[URL]', '[TITLE]')" onmouseout="addthis_close()" onclick="return addthis_sendto()"><img src="http://s9.addthis.com/button1-addthis.gif" alt="" border="0" height="16" width="125"></a>
"""

ADD_THIS_NO_HOVER = """
<a href="http://www.addthis.com/bookmark.php" onclick="return addthis_sendto()"><img src="http://s9.addthis.com/button1-addthis.gif" alt="" border="0" height="16" width="125"></a>
"""

ADD_THIS_POST = """
<script type="text/javascript" src="http://s7.addthis.com/js/152/addthis_widget.js"></script>"""


class AddThisNode(template.Node):
    def __init__(self, popup_on_hover):
        self.text = ADD_THIS_PRE
        if popup_on_hover:
            self.text += ADD_THIS_HOVER
        else:
            self.text += ADD_THIS_NO_HOVER
        self.text = mark_safe(self.text + ADD_THIS_POST)
    
    def render(self, context):
        return self.text
    

@register.tag(name="add_this")
def get_addthis_button(parser, token):
    split = token.split_contents()
    if len(split) == 1:
        tag_name = split[0]
    elif len(split) == 2:
        tag_name, popup_on_hover = split
    else:
        raise template.TemplateSyntaxError, "%r tag requires one or zero arguments" % token.contents.split()[0]
    
    if popup_on_hover and popup_on_hover not in ('hover', 'no-hover'):
        raise template.TemplateSyntaxError, "invalid argument to %r" % tag_name
    
    return AddThisNode(popup_on_hover == 'hover')




### static file URLs: change this if/when the static serving scheme changes

STATIC_FILE_KINDS = ('css', 'js', 'images', 'uploads')

class StaticFileURLNode(template.Node):
    def __init__(self, kind, name):
        self.kind = kind
        self.name = name
    
    def render(self, context):
        return '/static/%s/%s' % (self.kind, self.name)
    

@register.tag(name="static")
def get_static_file_link(parser, token):
    split = token.split_contents()
    if len(split) != 3:
        raise template.TemplateSyntaxError, "%r tag requires two arguments" % token.content.split[0]
    tag_name, kind, path = split
    if kind not in STATIC_FILE_KINDS:
        raise template.TemplatSyntaxError, "%r: invalid kind '%s'" % (tag_name, kind)
    return StaticFileURLNode(kind, path)
