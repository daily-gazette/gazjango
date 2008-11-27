from django.contrib.auth import decorators
from django.shortcuts    import get_object_or_404

from gazjango.accounts.models      import UserProfile
from gazjango.announcements.models import Announcement
from gazjango.articles.models      import StoryConcept

# =======================================
# = model getting / filtering functions =
# =======================================

def get_by_date_or_404(model, year, month, day, field='pub_date', **oth):
    d = oth
    d[field + '__year']  = int(year)
    d[field + '__month'] = int(month)
    d[field + '__day']   = int(day)
    return get_object_or_404(model, **d)

def filter_by_date(qset, year=None, month=None, day=None, field='pub_date', **oth):
    args = oth.copy()
    if year:
        args[field + '__year'] = int(year)
        if month:
            args[field + '__month'] = int(month)
            if day:
                args[field + '__day'] = int(day)
    return qset.filter(**args)


# ===============================
# = getting stuff from requests =
# ===============================

TRUE_VALUES = set(('yes', 'y', 'true', 't', 1))
FALSE_VALUES = set(('no', 'n', 'false', 'f', 0))
def boolean_arg(lookup, arg, default=False):
    """
    Casts `arg` (from `lookup`) to a boolean based on TRUE_VALUES and
    FALSE_VALUES, returning `default` if if it's uncertain.
    """
    try:
        val = lookup[arg].lower()
        if val in TRUE_VALUES:
            return True
        elif val in FALSE_VALUES:
            return False
        else:
            return default
    except KeyError:
        return default

def get_ip(request):
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        return request.META['HTTP_X_FORWARDED_FOR']
    elif 'REMOTE_ADDR' in request.META:
        return request.META['REMOTE_ADDR']
    else:
        return None

def get_user_profile(request):
    try:
        return request.user.get_profile()
    except (AttributeError, UserProfile.DoesNotExist):
        return None

ROBOT_UAS = ('Googlebot', 'Yahoo! Slurp', 'msnbot')
def is_robot(request):
    ua = request.META.get('HTTP_USER_AGENT', '')
    for robot in ROBOT_UAS:
        if robot in ua:
            return robot
    return None


# ===============
# = login stuff =
# ===============

staff_required = decorators.user_passes_test(lambda u: u.is_staff)


# ==============
# = miscellany =
# ==============

def reporter_admin_data(user):
    """
    Returns the data necessary just to render base.html of the 
    reporter admin.
    """
    articles = user.articles.all().order_by('-pub_date')
    announcements = Announcement.admin.order_by('-date_start')
    
    return {
        'announcement': announcements[0] if announcements.count() else None,
        'unclaimed': StoryConcept.unpublished.filter(users=None),
        'others': StoryConcept.unpublished.exclude(users=user).exclude(users=None)
    }
