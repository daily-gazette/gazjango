import datetime
import calendar
import re

from django.contrib.auth.decorators import permission_required
from django.views.decorators.cache  import cache_page
from django.db.models import Q
from django.template  import RequestContext
from django.http      import Http404, HttpResponse, HttpResponseRedirect
from django.core.urlresolvers   import reverse
from django.core.exceptions     import ObjectDoesNotExist
from django.shortcuts           import render_to_response, get_object_or_404
from gazjango.misc.view_helpers import get_by_date_or_404, filter_by_date, staff_required
from gazjango.misc.view_helpers import get_ip, get_user_profile

from gazjango.articles.models      import Article, Special, PhotoSpread, StoryConcept
from gazjango.articles.models      import Section, Subsection, Column
from gazjango.articles.forms       import SubmitStoryConcept,ConceptSaveForm
from gazjango.announcements.models import Announcement
from gazjango.comments.models      import PublicComment
from gazjango.comments.forms       import make_comment_form
from gazjango.issues.models        import Weather, WeatherJoke
from gazjango.jobs.models          import JobListing

from gazjango.scrapers.bico         import get_bico_news
from gazjango.scrapers.tla          import get_tla_links
from gazjango.scrapers.manual_links import manual_links, lca_links

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
        form = make_comment_form(logged_in=logged_in, initial=initial)
    
    try:
        photospread = story.photospread
    except PhotoSpread.DoesNotExist:
        return show_article(request, story, form, print_view)
    else:
        return show_photospread_page(request, photospread, num, form)

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
        'topstory': Article.published.get_top_story(),
        'other_comments': cs,
        'print_view': print_view,
        'comment_form': form
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
    
    data = { 'articles': articles, 'year': year, 'month': month, 'day': day,
             'section': section, 'subsection': subsection,
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


def homepage(request, template="index.html"):
    tops, mids, lows = Article.published.get_stories(num_mid=2, num_low=6)
    data = {
        'topstory': tops[0],
        'midstories': mids,
        'lowstories': lows,
        
        'comments': PublicComment.visible.order_by('-time').all()[:3],
        'weather': Weather.objects.for_today(),
        'joke': WeatherJoke.objects.latest(),
        
        'specials': Special.objects.order_by('-date').all()[:10],
        'announcements': Announcement.community.get_n(3),
        'jobs': JobListing.published.get_for_show(3),
        
        'bico_news': get_bico_news(),
        'tla_links': get_tla_links(),
        'manual_links': manual_links,
        'lca_links': lca_links,
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

@staff_required    
def staff_mail(request, template="staff/mail.html"):
    claimed, unclaimed = StoryConcept.unpublished.get_upcoming_concepts()
    admin_announcement = Announcement.admin.latest()
    data = {
        'minutes': admin_announcement,
        'unclaimed': unclaimed,
        'claimed': claimed,
    }
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)
 
@staff_required
def concept_save_page(request, template="staff/submit.html"):
    if request.method == 'POST':
        form = ConceptSaveForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            due = form.cleaned_data['due']
            users = form.cleaned_data['users']
            concept = StoryConcept.objects.get(name=name)
            
            concept.due = due
            concept.users = users
            concept.save()
            
            user = get_user_profile(request)
            personal, claimed, unclaimed = StoryConcept.unpublished.get_concepts(user=user)
            admin_announcement = Announcement.admin.latest()
            form = SubmitStoryConcept()
            data = {
                'form': form,
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
        
        name = concept.name
        due  = concept.due
        users= concept.users
        
        form = ConceptSaveForm(
            initial={
                'name': name,
                'due':due,
                'users': users,
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
    
    tops, mids, lows = sec.get_stories(num_top=2, num_mid=3, num_low=12)
    num_low_lists = 4
    lowlist = [ [] for i in range(num_low_lists) ]
    for i in range(len(lows)):
        lowlist[i % num_low_lists].append(lows[i])
    
    data = {
        'section': sec,
        'stories': tops + mids + lows,
        'topstories': tops,
        'midstories': mids,
        'lowlist': lowlist,
        'comments': PublicComment.visible.filter(article__section=sec).order_by('-time')
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
            'comments': PublicComment.visible.filter(article__subsection=sub).order_by('-time')
        }
        return render_to_response('sections/sub_stuco-platforms.html',
                                  context_instance=RequestContext(request, data))
    
    else:
        tops, mids, lows = sub.get_stories(num_top=2, num_mid=3, num_low=12)
        num_low_lists = 4
        lowlist = [ [] for i in range(num_low_lists) ]
        for i in range(len(lows)):
            lowlist[i % num_low_lists].append(lows[i])
    
        comments = PublicComment.visible.filter(article__subsection=sub)
        data = {
            'section': sec,
            'subsection': sub,
            'recent_stories': sub.published_articles().order_by('-pub_date')[:10],
            'topstories': tops,
            'midstories': mids,
            'lowlist': lowlist,
            'comments': comments.order_by('-time')
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
