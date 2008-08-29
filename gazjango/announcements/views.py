from django.http     import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts         import render_to_response, get_object_or_404
from misc.view_helpers        import filter_by_date
from announcements.models import Announcement
from announcements.forms  import SubmitAnnouncementForm
from articles.models      import Article
from comments.models      import PublicComment

def announcement(request, slug, year, month=None, day=None):
    an = get_object_or_404(Announcement, slug=slug, date_start__year=year)
    top, mids, lows = Article.published.get_stories(num_top=1, num_mid=3, num_low=0)
    data = {
        'announcement': an,
        'topstory': top[0],
        'stories': mids,
        'announcements': Announcement.community.order_by('-date_end')[:4],
        'comments': PublicComment.visible.order_by('-time')[:3]
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

def submit_announcement(request, template="announcements/submit.html"):
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


def announcement_success(request, template="announcements/success.html"):
    return render_to_response(template, {}, context_instance=RequestContext(request))
