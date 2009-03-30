from django.http     import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers   import reverse
from django.shortcuts           import render_to_response, get_object_or_404
from gazjango.misc.view_helpers import filter_by_date
from gazjango.announcements.models import Announcement
from gazjango.announcements.forms  import SubmitAnnouncementForm
import datetime

def announcement(request, slug, year, month=None, day=None):
    an = get_object_or_404(Announcement, slug=slug, date_start__year=year)
    data = {
        'announcement': an,
        'recent_announcements': Announcement.community.order_by('-date_end')[:4],
    }
    rc = RequestContext(request)
    return render_to_response("listings/announcements/details.html", data, context_instance=rc)


def list_announcements(request, kind=None, year=None, month=None, day=None, order='d'):
    if (request.GET.get('order', None) or order).startswith('d'):
        qset = Announcement.community.order_by('-date_end', '-date_start')
    else:
        qset = Announcement.community.order_by('date_end', 'date_start')
    
    if year:
        qset = filter_by_date(qset, year, month, day, field='date_start')
    else:
        qset = qset.exclude(date_start__gt=datetime.date.today())
    
    if kind:
        qset = qset.filter(kind=kind)
    
    events = qset.exclude(event_date=None)
    non_events = qset.filter(event_date=None)
    
    data = { 
        'announcements': qset,
        'kind': kind,
        'year': year,
        'month': month,
        'day': day,
        'events': events.order_by('event_date', 'event_time', 'pk'),
        'non_events': non_events,
        'recent_announcements': Announcement.community.order_by('-date_end')[:4],
    }
    rc = RequestContext(request)
    return render_to_response("listings/announcements/list.html", data, context_instance=rc)

def submit_announcement(request, template="listings/announcements/submit.html"):
    if request.method == 'POST':
        form = SubmitAnnouncementForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(announcement_success))
    else:
        form = SubmitAnnouncementForm()
    
    data = { 'form': form }
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)


def announcement_success(request, template="listings/announcements/success.html"):
    return render_to_response(template, {}, context_instance=RequestContext(request))
