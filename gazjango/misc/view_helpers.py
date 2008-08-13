from django.shortcuts import get_object_or_404

from announcements.models import Announcement
from articles.models      import StoryConcept

def get_by_date_or_404(model, year, month, day, field='pub_date', **oth):
    d = oth
    d[field + '__year']  = int(year)
    d[field + '__month'] = int(month)
    d[field + '__day']   = int(day)
    return get_object_or_404(model, **d)

def filter_by_date(qset, year=None, month=None, day=None, field='pub_date'):
    args = {}
    if year:
        args[field + '__year'] = int(year)
        if month:
            args[field + '__month'] = int(month)
            if day:
                args[field + '__day'] = int(day)
    return qset.filter(**args)


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
