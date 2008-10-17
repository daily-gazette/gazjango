import datetime

from django.contrib.auth.decorators import permission_required
from django.template            import RequestContext
from django.shortcuts           import render_to_response, get_object_or_404
from django.http                import Http404, HttpResponse, HttpResponseRedirect
from django.utils.html          import escape
from gazjango.misc.view_helpers import get_by_date_or_404, filter_by_date, reporter_admin_data

from gazjango.articles.models      import Article, Special, PhotoSpread, StoryConcept
from gazjango.articles.models      import Section, Subsection, Column
from gazjango.announcements.models import Announcement
from gazjango.comments.models      import PublicComment
from gazjango.comments.forms       import CommentForm, make_comment_form
from gazjango.issues.models        import Weather, WeatherJoke
from gazjango.jobs.models          import JobListing
from gazjango.tagging.models       import TagGroup, Tag

from gazjango.scrapers.bico         import get_bico_news
from gazjango.scrapers.tla          import get_tla_links
from gazjango.scrapers.manual_links import manual_links, lca_links


def article(request, slug, year, month, day, num=None, form=None, print_view=False):
    "Base function to call for displaying a given article."
    story = get_by_date_or_404(Article, year, month, day, slug=slug)
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
    user = request.user.get_profile() if request.user.is_authenticated() else None
    ip = request.META['REMOTE_ADDR']
    context = RequestContext(request, {
        'story': story,
        'comments': PublicComment.objects.for_article(story, user, ip),
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
    
    user = request.user.get_profile() if user.is_authenticated() else None
    ip = request.META['REMOTE_ADDR']
    
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


def post_comment(request, slug, year, month, day):
    story = get_by_date_or_404(Article, year, month, day, slug=slug)
    
    logged_in = request.user.is_authenticated()
    form = make_comment_form(data=request.POST, logged_in=logged_in)
    
    if form.is_valid():
        args = {
            'subject': story,
            'text': escape(form.cleaned_data['text']).replace("\n", "<br/>"),
            'ip_address': request.META['REMOTE_ADDR'],
            'user_agent': request.META['HTTP_USER_AGENT']
        }
        
        data = form.cleaned_data
        if logged_in:
            args['user'] = request.user.get_profile()
            if data['anonymous'] and data['name'] != request.user.get_full_name():
                args['name'] = data['name']
        else:
            args['name']  = data['name']
            args['email'] = data['email']
        
        comment = PublicComment.objects.new(**args)
        
        if request.is_ajax():
            return HttpResponse('success')
        else:
            return HttpResponseRedirect(comment.get_absolute_url())
    else:
        if request.is_ajax():
            template = "stories/comment_form.html"
            rc = RequestContext(request, { 'comment_form': form })
            return render_to_response(template, context_instance=rc)
        else:
            return specific_article(request, story, form=form)


def archives(request, section=None, subsection=None, year=None, month=None, day=None):
    articles = filter_by_date(Article.published, year, month, day)
    if section:
        section = get_object_or_404(Section, slug=section)
        articles = articles.filter(section=section)
    if subsection:
        subsection = get_object_or_404(Subsection, section=section, slug=subsection)
        articles = articles.filter(subsection=subsection)
    
    template = (
        'archives/for_sub_%s.html' % subsection.slug if subsection else '',
        'archives/for_sec_%s.html' % section.slug if section else '',
        'archives/generic.html'
    )
    
    data = { 'articles': articles, 'year': year, 'month': month, 'day': day,
             'section': section, 'subsection': subsection }
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
        'jobs': JobListing.unfilled.order_by('-pub_date')[:3],
        
        'bico_news': get_bico_news(),
        'tla_links': get_tla_links(),
        'manual_links': manual_links,
        'lca_links': lca_links
    }
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)


search        = lambda request, **kwargs: render_to_response("base.html", locals())
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
        'topstories': tops,
        'midstories': mids,
        'lowlist': lowlist,
        'comments': PublicComment.visible.filter(article__section=sec).order_by('-time')
    }
    
    if sec.slug == 'opinions':
        data['columns'] = Column.objects.order_by('-year', '-semester', 'name')
        f = data['columns'][0]
        data['curr_columns'] = data['columns'].filter(year=f.year, semester=f.semester)
    
    template = ("sections/sec_%s.html" % section,
                "sections/section.html")
    rc = RequestContext(request, data)
    return render_to_response(template, context_instance=rc)


def subsection(request, section, subsection):
    sec = get_object_or_404(Section, slug=section)
    sub = get_object_or_404(Subsection, section=sec, slug=subsection)
    
    tops, mids, lows = sub.get_stories(num_top=2, num_mid=3, num_low=12)
    num_low_lists = 4
    lowlist = [ [] for i in range(num_low_lists) ]
    for i in range(len(lows)):
        lowlist[i % num_low_lists].append(lows[i])
    
    data = {
        'section': sec,
        'subsection': sub,
        'recent_stories': sub.articles.all().order_by('-pub_date')[:10],
        'topstories': tops,
        'midstories': mids,
        'lowlist': lowlist,
        'comments': PublicComment.visible.filter(article__subsection=sub).order_by('-time')
    }
    try:
        column = sub.column
    except Column.DoesNotExist:
        pass
    else:
        data['column'] = column
        data['columns'] = Column.objects.order_by('-year', '-semester')
    
    template = ("sections/sub_%s.html" % sub.slug,
                "sections/sub_of_%s.html" % sec.slug,
                "sections/subsection.html")
    
    rc = RequestContext(request, data)
    return render_to_response(template, context_instance=rc)



@permission_required('accounts.can_access_admin')
def admin_write_page1(request, template="custom-admin/write_page1.html"):
    data = reporter_admin_data(request.user.get_profile())
    data['sections' ] = Section.objects.all()
    data['taggroups'] = TagGroup.objects.all()
    data['loosetags'] = Tag.objects.filter(group=None)
    
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)


def list_subsections(request, section):
    """
    Lists the subsections in a given section, in a plaintext format that
    looks like "fac_staff | Faculty & Staff". (For AJAX requests.)
    """
    subs = get_object_or_404(Section, slug=section).subsections.filter(is_over=False)
    data = ["%s | %s" % (sub.slug, sub.name) for sub in subs]
    return HttpResponse('\n'.join(data))
