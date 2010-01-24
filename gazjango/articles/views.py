from collections import defaultdict
import datetime
import calendar
import heapq
import re

from django.contrib.auth.decorators import permission_required
from django.views.decorators.cache  import cache_page
from django.db.models import Q
from django.template  import RequestContext
from django.http      import Http404, HttpResponse, HttpResponseRedirect
from django.core.urlresolvers   import reverse
from django.core.exceptions     import ObjectDoesNotExist
from django.shortcuts           import render_to_response, get_object_or_404
from gazjango.misc.helpers      import is_from_swat
from gazjango.misc.view_helpers import get_by_date_or_404, filter_by_date, staff_required, \
                                       get_ip, get_user_profile

from gazjango.ads.models                import TextLinkAd, BannerAd
from gazjango.articles.models           import Article, Special, PhotoSpread, StoryConcept, \
                                               Section, Subsection, Column
from gazjango.articles.forms            import SubmitStoryConcept,ConceptSaveForm
from gazjango.announcements.models      import Announcement,Poster
from gazjango.comments.models           import PublicComment
from gazjango.comments.forms            import make_comment_form
from gazjango.issues.models             import Weather, WeatherJoke
from gazjango.jobs.models               import JobListing
from gazjango.accounts.models           import UserProfile
from gazjango.community.models          import Entry
from gazjango.community.sources.flickr  import FlickrPhoto

from gazjango.scrapers.bico         import get_bico_news

def article(request, slug, year, month, day, num=None, form=None, print_view=False):
    "Base function to call for displaying a given article."
    kwargs = { 'slug': slug[:100] } # for very-long old slugs
    if not request.user.is_staff:
        kwargs['status'] = 'p' # allow previews for staff
    story = get_by_date_or_404(Article, year, month, day, **kwargs)
    return specific_article(request, story, num, form, print_view)

def specific_article(request, story, num=None, form=None, print_view=False):
    "Displays an article without searching the db for it."
    
    logged_in = request.user.is_authenticated()
    if form is None:
        initial = { 'text': 'Have your say.' }
        if logged_in:
            initial['name'] = request.user.get_full_name()
        staff = logged_in and get_user_profile(request).staff_status()
        form = make_comment_form(logged_in=logged_in, initial=initial, staff=staff)
    
    if story.is_swat_only():
        if not is_from_swat(user=get_user_profile(request), ip=get_ip(request)):
            return show_swat_only(request, story)
    
    try:
        photospread = story.photospread
    except PhotoSpread.DoesNotExist:
        return show_article(request, story, form, print_view)
    else:
        return show_photospread_page(request, photospread, num, form)

def show_swat_only(request, story, template='stories/swat_only.html'):
    """Shows a "sorry, you can't see this story" message."""
    return render_to_response(template, context_instance=RequestContext(request, {
        'story': story,
        'recent_stories': Article.published.order_by('-pub_date')[:3],
        'posters': Poster.published.get_n(1),
        'related': story.related_list(3),
        
        'base_template': 'stories/view.html',
        'print_view': False,
        
        'top_banner': BannerAd.article_top.pick(allow_zero_priority=False)
    }))

def show_article(request, story, form, print_view=False):
    "Shows the requested article."
    d = story.pub_date
    template = (
        "stories/view_%s_%s_%s_%s.html" % (d.year, d.month, d.day, story.slug),
        "stories/view_from_sub_%s.html" % story.subsection.slug if story.subsection else '',
        "stories/view_from_sec_%s.html" % story.section.slug,
        "stories/view.html"
    )
    
    cs = PublicComment.visible.order_by('-time').exclude(article=story)
    
    user = get_user_profile(request)
    ip = get_ip(request)
    comments = PublicComment.objects.for_article(story, user, ip)
    
    context = RequestContext(request, {
        'story': story,
        'comments': comments,
        'related': story.related_list(3),
        # 'topstory': Article.published.get_top_story(),
        # 'other_comments': cs,
        'print_view': print_view,
        'comment_form': form,
        'posters': Poster.published.get_n(1),
        'recent_stories': Article.published.order_by('-pub_date')[:3],
        
        'top_banner': BannerAd.article_top.pick(allow_zero_priority=False),
    })
    return render_to_response(template, context_instance=context)


def show_photospread_page(request, spread, num=None, form=None, whole_page=None):
    if num is None:
        num = 1
    
    page = spread.get_photo_number(num)
    if not page:
        raise Http404('This photospread does not have a photo number "%s".' % num)
    
    data = {
        'story': spread,
        'page': page,
        'next': page.next(),
        'prev': page.prev()
    }
    
    if whole_page is None:
        whole_page = not request.is_ajax()
    
    user = get_user_profile(request)
    ip = get_ip(request)
    
    if whole_page:
        data.update(
            related=spread.related_list(3),
            topstory=Article.published.get_top_story(),
            comments=PublicComment.objects.for_article(spread, user, ip),
            other_comments=PublicComment.visible.order_by('-time').exclude(article=spread),
            comment_form=form
        )
        template = "stories/photospread.html"
    else:
        template = "stories/photo.html"
    
    rc = RequestContext(request, data)
    return render_to_response(template, context_instance=rc)


def archives(request, section=None, subsection=None, year=None, month=None, day=None):
    articles = filter_by_date(Article.published, year, month, day)
    if section:
        section = get_object_or_404(Section, slug=section)
        articles = articles.filter(section=section)
    if subsection:
        subsection = get_object_or_404(Subsection, section=section, slug=subsection)
        articles = articles.filter(section=section, subsection=subsection)
    articles = articles.order_by('pub_date')
    
    data = { 'articles': articles,
             'year': year,
             'month': month,
             'day': day,
             'section': section,
             'subsection': subsection,
             'posters': Poster.published.get_n(1),
             'sections': Section.objects.all() }
    
    if day:
        template = 'archives/by_day.html'
    elif month:
        template = 'archives/by_month.html'
    else:
        pub_dates = articles.values_list('pub_date', flat=True)
        dates = set([datetime.date(d.year, d.month, d.day) for d in pub_dates])
        
        if not dates:
            # screw reverse, this place is brittle
            url = '/archives/'
            if section:    url += section.slug + '/'
            if subsection: url += subsection.slug + '/'
            if year:       url += year + '/'
            split = url.split('/')
            if len(split) > 3:
                return HttpResponseRedirect('/'.join(split[:-2] + ['']))
            else: # no articles at all? really?
                raise Http404
        
        if year:
            start_date = datetime.date(int(year), 1, 1)
            end_date = datetime.date(int(year), 12, 31)
        else:
            start_date = min(dates)
            end_date = max(dates)
        
        calendar.setfirstweekday(calendar.SUNDAY)
        
        year_i, month_i = (end_date.year, end_date.month)
        cal = [ (year_i, month_i, calendar.monthcalendar(year_i, month_i)) ]
        while year_i > start_date.year or month_i > start_date.month:
            month_i -= 1
            if month_i < 1:
                month_i = 12
                year_i -= 1
            cal.append( (year_i, month_i, calendar.monthcalendar(year_i, month_i)) )
        
        weekdays = range(7)
        for year_i, month_i, month_cal in cal:
            for week in month_cal:
                for i in weekdays:
                    if week[i] and datetime.date(year_i, month_i, week[i]) not in dates:
                        week[i] *= -1
        
        data['calendar'] = cal
        
        data['url_base'] = '/archives'
        if section:
            data['url_base'] += '/' + section.slug
            if subsection:
                data['url_base'] += '/' + subsection.slug
        
        template = 'archives/generic.html'
    
    rc = RequestContext(request, data)
    
    return render_to_response(template, context_instance=rc)


def homepage(request, social_len=7, num_tweets=2, template="index.html"):
    recent_comments = PublicComment.visible.order_by('-time')[:50]
    
    # creating the social stream
    non_tweets = Entry.published.get_entries(num=social_len, exclusion="tweet")
    tweets = Entry.published.get_entries(num=num_tweets, category="tweet")
    
    stream = heapq.nlargest(social_len,
       [("entry", entry) for entry in non_tweets] +
       [("entry", entry) for entry in tweets] +
       [("comment", comment) for comment in recent_comments[:2]],
       key=lambda (kind, obj): obj.timestamp if kind == "entry" else obj.time
    )
    
    # getting the highlighted comment
    top_comment = max(recent_comments, key=PublicComment.num_upvotes)            
            
    # getting comment list for facebook-style listings
    comment_list = defaultdict(list)
    for comment in recent_comments[:20]:
        comment_list[comment.subject].insert(0, comment)
    sorted_comment_list = sorted(comment_list.values(), key=lambda lst: lst[-1].time, reverse=True)
    
    # sorting events and announcements
    events = Announcement.events.order_by('event_date', 'event_time', 'pk')
    announcements = Announcement.regular.order_by('-date_end', '-date_start')    
    
    data = {
        'topstories': Article.published.filter(position='1').order_by('-pub_date')[:6],
        'stories': Article.published.order_by('-pub_date')[:4],
        
        'weather': Weather.objects.for_today(),
        'joke': WeatherJoke.objects.latest(),
        
        'specials': Special.objects.order_by('-date').all()[:10],
        'announcements': announcements[:9],
        'events':events[:5],
        'jobs': JobListing.published.get_for_show(3),
        
        'bico_news': get_bico_news(),
        'text_link_ads': [ad.render() for ad in TextLinkAd.objects.all()],
        'banner_ad': BannerAd.front.pick(),
        
        'stream':stream,
        'top_comment':top_comment,
        'sorted_comment_list':sorted_comment_list,
    }
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)
    
def april_fools(request, template="aprilfools.html"):
    section = 'features'
    subsection = 'april-fools'
    
    sec = get_object_or_404(Section, slug=section)
    sub = get_object_or_404(Subsection, section=sec, slug=subsection)
    
    tops, mids, lows = sub.get_stories(num_top=2,num_mid=4, num_low=3)
    data = {
        'topstories': tops,
        'midstories': mids,
        'lowstories': lows,
        'announcements': Announcement.community.get_n(3),
        'bico_news': get_bico_news(),
        # 'tla_links': get_tla_links(),
        # 'manual_links': manual_links,
        # 'lca_links': lca_links,
    }
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)

@staff_required
def staff(request,  template="staff/index.html"):
    user = get_user_profile(request)
    personal, claimed, unclaimed = StoryConcept.unpublished.get_concepts(user=user)
    admin_announcement = Announcement.admin.latest()
    if request.method == 'POST':
        form = SubmitStoryConcept(request.POST)
        if form.is_valid():
            concept = form.save(commit=False)
            concept.save()
            form.save_m2m()
            return HttpResponseRedirect(reverse(staff))
    else:
        form = SubmitStoryConcept()
    data = {
        'form': form,
        'minutes': admin_announcement,
        'personal': personal,
        'unclaimed': unclaimed,
        'claimed': claimed,
        'author': user,
		'unpublished_stories': Article.objects.exclude(status='p')
    }
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)

def staff_mail(request, template="staff/mail.html"):
    claimed, unclaimed = StoryConcept.unpublished.get_upcoming_concepts()
    
    admin_announcement = Announcement.admin.latest()
    if (datetime.date.today() - admin_announcement.date_end) > datetime.timedelta(weeks=2):
        admin_announcement = None
    
    if not (len(claimed) or len(unclaimed) or admin_announcement):
        raise Http404("No content.")
    
    data = {
        'minutes': admin_announcement,
        'unclaimed': unclaimed,
        'claimed': claimed,
    }
    return render_to_response(template, data)
 
@staff_required
def concept_save_page(request, template="staff/submit.html"):
    if request.method == 'POST':
        form = ConceptSaveForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['due']:
                due = form.cleaned_data['due']
            else:
                due = ""
                
            if form.cleaned_data['notes']:
                notes = form.cleaned_data['notes']
            else:
                notes = ""
            name = form.cleaned_data['name']
            
            concept = StoryConcept.objects.get(name=name)
            
            concept.due = due
            concept.notes = notes
            
            concept.save()
            
            user = get_user_profile(request)
            personal, claimed, unclaimed = StoryConcept.unpublished.get_concepts(user=user)
            admin_announcement = Announcement.admin.latest()
            newform = SubmitStoryConcept()
            data = {
                'form': newform,
                'minutes': admin_announcement,
                'personal': personal,
                'unclaimed': unclaimed,
                'claimed': [concept],
                'author': user,
        		'unpublished_stories': Article.objects.exclude(status='p')
            }
            rc = RequestContext(request)
            return render_to_response("staff/index.html", data, context_instance=rc)
        else:
            return HttpResponse('failure')
    elif request.GET.has_key('name'):
        story_name = request.GET.get('name')
        concept = StoryConcept.objects.get(name=story_name)
        
        form = ConceptSaveForm(
            initial={
                'name': concept.name,
                'due': concept.due,
                'notes': concept.notes
            }
        )
        data = {
            'form': form,
        }
        rc = RequestContext(request)
        return render_to_response("staff/concept_save_form.html", data, context_instance=rc)
    else:
        form = ConceptSaveForm()
        data = { 'form': form }
        rc = RequestContext(request)
        return render_to_response(template, data, context_instance=rc)
    
def search(request):
    "Temporary: redirect to Google search. :/"
    s = request.GET.get('s', '')
    url = "http://www.google.com/search?hl=en&q=%s+site:daily.swarthmore.edu" % s
    return HttpResponseRedirect(url)

email_article = lambda request, **kwargs: render_to_response("base.html", locals())


def section(request, section):
    sec = get_object_or_404(Section, slug=section)
    
    tops, mids, lows = sec.get_stories(num_top=4, num_mid=6, num_low=12)
    num_low_lists = 4
    lowlist = [ [] for i in range(num_low_lists) ]
    for i in range(len(lows)):
        lowlist[i % num_low_lists].append(lows[i])
        
        
    entries = Entry.published.get_entries(num=9)
    comments = PublicComment.visible.filter(article__section=sec).order_by('-time').all()[:20]
    
    stream = heapq.nlargest(9,
       [("entry", entry) for entry in entries] + [("comment", comment) for comment in comments],
       key=lambda (kind, obj): obj.timestamp if kind == "entry" else obj.time
    )
    
    rec_multi_story, rec_multi = Article.published.get_recent_multimedia(
        base=sec.articles,
        exclude=[a.main_image for a in tops])
    
    data = {
        'section': sec,
        'stories': tops + mids + lows,
        'topstories': tops,
        'midstories': mids,
        'lowlist': lowlist,
        'stream': stream,
        'comments': PublicComment.visible.filter(article__section=sec).order_by('-time'),
        'rec_multi': rec_multi or 'none',
        'rec_multi_story': rec_multi_story,
    }
    
    if sec.slug == 'opinions':
        data['columns'] = [
            column for column
            in Column.objects.order_by('-year', '-semester', 'name').select_related(depth=1)
            if column.articles.filter(status='p').count() > 0
        ]
        f = data['columns'][0]
        data['curr_columns'] = [column for column in data['columns']
                                if column.year == f.year and column.semester == f.semester]
    
    template = ("sections/sec_%s.html" % section,
                "sections/section.html")
    rc = RequestContext(request, data)
    return render_to_response(template, context_instance=rc)


def subsection(request, section, subsection):
    sec = get_object_or_404(Section, slug=section)
    sub = get_object_or_404(Subsection, section=sec, slug=subsection)
    
    comments = PublicComment.visible.filter(article__subsection=sub)
    stream = comments[:5]
    
    if sub.slug == 'stuco-platforms':
        articles = sub.published_articles()
        latest = articles.latest()
        cutoff = latest.pub_date - datetime.timedelta(days=7)
        
        # there shouldn't be too many and we're showing them all: do some processing
        current = []
        sep = re.compile(r',|:')
        for art in articles.filter(pub_date__gte=cutoff):
            pos, name = [x.strip() for x in sep.split(art.headline + ',', 1)]
            if name.endswith(','):
                name = name[:-1]
            current.append( (pos, name, art) )
        # sort by position then last name
        current.sort(key=lambda t: (t[0], t[1].split(None, 1)[1]))
        
        data = {
            'section': sec,
            'subsection': sub,
            'platforms': current,
            'latest': latest,
            'stream': stream,
        }
        return render_to_response('sections/sub_stuco-platforms.html',
                                  context_instance=RequestContext(request, data))
    
    else:
        tops, mids, lows = sub.get_stories(num_top=2, num_mid=3, num_low=12)
        num_low_lists = 4
        lowlist = [ [] for i in range(num_low_lists) ]
        for i in range(len(lows)):
            lowlist[i % num_low_lists].append(lows[i])
    
        comments = PublicComment.visible.filter(article__subsection=sub).order_by('-time')
        stream = comments[:4]
        
        rec_multi_story, rec_multi = Article.published.get_recent_multimedia(
            base=sub.articles,
            exclude=[a.main_image for a in tops])
        
        data = {
            'section': sec,
            'subsection': sub,
            'recent_stories': sub.published_articles().order_by('-pub_date')[:12],
            'topstories': tops,
            'midstories': mids,
            'lowlist': lowlist,
            'stream': stream,
            'rec_multi': rec_multi or 'none',
            'rec_multi_story': rec_multi_story,
        }
        try:
            column = sub.column
        except Column.DoesNotExist:
            pass
        else:
            data['column'] = column
            data['columns'] = Column.objects.order_by('-year', '-semester', 'name')
        
        template = ("sections/sub_%s.html" % sub.slug,
                    "sections/sub_of_%s.html" % sec.slug,
                    "sections/subsection.html")
        
        rc = RequestContext(request, data)
        return render_to_response(template, context_instance=rc)


def list_subsections(request, section):
    """
    Lists the subsections in a given section, in a plaintext format that
    looks like "fac_staff | Faculty & Staff". (For AJAX requests.)
    """
    subs = get_object_or_404(Section, slug=section).subsections
    data = ["%s | %s" % (sub.slug, sub.name) for sub in subs]
    return HttpResponse('\n'.join(data))
