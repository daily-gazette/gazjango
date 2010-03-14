from django.http                   import HttpResponseRedirect, Http404
from django.template               import RequestContext
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers      import reverse
from django.shortcuts              import render_to_response, get_object_or_404

from gazjango.misc.view_helpers    import get_by_date_or_404, filter_by_date
from gazjango.announcements.models import Announcement, Poster
from gazjango.announcements.forms  import SubmitAnnouncementForm, SubmitPosterForm
from gazjango.articles.models      import Article
from gazjango.issues.models        import Issue, Menu, Event
from gazjango.jobs.models          import JobListing
from gazjango.jobs.forms           import SubmitJobForm
from gazjango.comments.models      import PublicComment
from gazjango.reviews.directions   import TRAIN_STATIONS
from gazjango.reviews.models       import Establishment, Review
from gazjango.reviews.forms        import SubmitEstablishmentForm, SubmitReviewForm
from gazjango.housing.models       import HousingListing
from gazjango.housing.forms        import SubmitHousingForm
from gazjango.misc.view_helpers    import get_user_profile
from gazjango.misc.files           import handle_file_upload
from gazjango.scrapers.bico        import get_bico_news
from gazjango.media.models         import ImageFile, MediaBucket

import datetime
import itertools

def announcement(request, slug, year, month=None, day=None):
    an = get_object_or_404(Announcement, slug=slug, date_start__year=year)
    data = {
        'announcement': an,
        'recent_announcements': Announcement.community.order_by('-date_end')[:4],
        'poster': Poster.published.get_running(),
    }
    rc = RequestContext(request)
    return render_to_response("listings/announcements/details.html", data, context_instance=rc)


def list_announcements(request):
    regular = Announcement.regular.all().order_by('-date_end', '-date_start')
    lost_and_found = Announcement.lost_and_found.now_running().order_by('-date_start')
    
    # get the five most recent days with announcements, starting with today
    today = datetime.date.today()
    event_days = Announcement.events.filter(event_date__gte=today).order_by('event_date') \
                                    .values_list('event_date', flat=True).distinct()[:5]
    if len(event_days) < 5:
        event_days = Announcement.events.all().order_by('-event_date') \
                                 .values_list('event_date', flat=True).distinct()[:5]
    
    # get the actual announcements from those days
    # mysql doesn't actually support this fancy query, so listify it
    events = Announcement.events.filter(event_date__in=list(event_days)) \
                                .order_by('event_date', 'event_time')
    event_list = [(date, list(evs)) for date, evs in itertools.groupby(events, lambda e: e.event_date)]
    
    data = {
        'event_list': event_list,
        'regular': regular,
        'lost_and_found': lost_and_found[:10],
        'poster': Poster.published.get_running(),
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
    
    return render_to_response(template, context_instance=RequestContext(request, {
        'form': form,
        'poster': Poster.published.get_running(),
    }))


def announcement_success(request, template="listings/announcements/success.html"):
    return render_to_response(template, context_instance=RequestContext(request, {
        'poster': Poster.published.get_running(),
    }))

@login_required
def submit_poster(request, template="listings/posters/submit.html"):
    if request.method == 'POST':
        form = SubmitPosterForm(request.POST, request.FILES)
        if form.is_valid():
            profile = get_user_profile(request)
            
            args = dict( (k, v) for k, v in form.cleaned_data.items() if k != 'poster' )
            poster = Poster(**args)
            poster.sponsor_user = profile
            
            poster_file_path = handle_file_upload(request.FILES['poster'], 'posters')
            poster.poster = ImageFile.objects.create(
                name = poster.title,
                slug = slugify(poster.title),
                bucket = MediaBucket.objects.get_or_create(slug="posters", defaults={
                    'name': "Posters",
                    'description': "Posters uploaded by the community."
                })[0],
                license_type='p',
                data=poster_file_path,
            )
            poster.poster.users = [profile]
            
            poster.save()
            return HttpResponseRedirect(reverse(poster_success))
    else:
        form = SubmitPosterForm()
    
    return render_to_response(template, context_instance=RequestContext(request, {
        'form': form,
        'poster': Poster.published.get_running(),
    }))

def poster_success(request, template="listings/posters/success.html"):
    return render_to_response(template, context_instance=RequestContext(request, {
        'poster': Poster.published.get_running(),
    }))


def around_swarthmore(request,template = "listings/around/index.html"):
    today = datetime.date.today()
    year = today.year
    month = today.month
    day = today.day
    
    date = datetime.date(int(year), int(month), int(day))
    current = Announcement.community.filter(date_start__lte=date, date_end__gte=date)

    regular = current.filter(is_lost_and_found=False, event_date=None)
    events = current.exclude(event_date=None)
    lost_and_found = current.filter(is_lost_and_found=True)

    one_week = datetime.timedelta(days=7)
    if date == datetime.date.today():
        jobs = JobListing.unfilled.get_for_show(num=5, cutoff=one_week)
    else:
        jobs = JobListing.published.get_for_show(num=5, base_date=date, cutoff=one_week)

    if not current.count() and not jobs.count():
        raise Http404

    tomorrow = date + datetime.timedelta(days=1)
    comments = PublicComment.visible.filter(time__lt=tomorrow).order_by('-time')

    t,m,l = Article.published.get_stories(num_top=0, num_mid=4, num_low=0)
        
    if request.method == 'POST':
        announcement_form = SubmitAnnouncementForm()
        job_form = SubmitJobForm()
        
        if announcement_form.is_valid():
            announcement_form.save_m2m()
            return HttpResponseRedirect(reverse(around_swarthmore))
            
        if job_form.is_valid():
            job_form.save_m2m()
            return HttpResponseRedirect(reverse(around_swarthmore))
    else:
        announcement_form = SubmitAnnouncementForm()
        job_form = SubmitJobForm()
        
    if datetime.datetime.now().hour < 21:
        menu = Menu.objects.for_today()
    else:
        menu = Menu.objects.for_tomorrow()

    data = {
        'year': year, 'month': month, 'day': day,
        'date': date,
        'announcements': regular.order_by('-date_start', 'pk'),
        'events': events.order_by('event_date', 'event_time', 'pk'),
        'lost_and_found': lost_and_found.order_by('-date_start', 'pk'),
        'jobs': jobs,
        'comments': comments[:10],
        'stories': m,
        'announcement_form': announcement_form,
        'job_form': job_form,
        'menu': menu,
        'bico_news': get_bico_news(),
        'poster': Poster.published.get_running(),
    }
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)
