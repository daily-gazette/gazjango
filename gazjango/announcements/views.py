from django.template  import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from helpers          import filter_by_date
from announcements.models import Announcement
from articles.models      import Article

def announcement(request, slug, year, month=None, day=None):
    an = get_object_or_404(Announcement, slug=slug, date_start__year=year)
    data = {
        'announcement': an,
        'topstory': Article.published.get_top_story()
    }
    rc = RequestContext(request)
    return render_to_response("announcements/details.html", data, context_instance=rc)


def list_announcements(request, kind=None, year=None, month=None, day=None, order='a'):
    if (request.GET.get('order', None) or order).startswith('d'):
        qset = Announcement.published.order_by('-date_end', '-date_start')
    else:
        qset = Announcement.published.order_by('date_end', 'date_start')
    
    if kind:
        qset = qset.filter(kind=kind)
    
    data = { 
        'announcements': filter_by_date(qset, year, month, day),
        'kind': kind,
        'year': year,
        'month': month,
        'day': day
    }
    rc = RequestContext(request)
    return render_to_response("announcements/list.html", data, context_instance=rc)
