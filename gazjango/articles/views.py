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
    template = [
        "stories/view_%s_%s_%s_%s.html" % (d.year, d.month, d.day, story.slug),
    ]
    for sub in story.subsections.all():
        template.append("stories/view_from_sub_%s.html" % sub.slug)
    template.extend([
        "stories/view_from_sec_%s.html" % story.section.slug,
        "stories/view.html"
    ])
    
    cs = PublicComment.visible.order_by('-time').exclude(article=story)
    context = RequestContext(request, {
        'story': story,
        'comments': story.comments.all(),
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
    
    if whole_page:
        data.update(
            related=spread.related_list(3),
            topstory=Article.published.get_top_story(),
            comments=spread.comments.all(),
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


def show_comments(request, slug, year, month, day, num=None):
    """
    Returns the comments for the specified articles, rendered as they are
    on article view pages, starting after number `num`. Used for after
    you've posted an AJAX comment.
    """
    story = get_by_date_or_404(Article, year, month, day, slug=slug)
    comments = story.comments.filter(number__gt=num or 0)
    rc = RequestContext(request, { 'comments': comments, 'new': True })
    return render_to_response("stories/comments.html", context_instance=rc)



def articles(request, year=None, month=None, day=None, template="archives.html"):
    articles = filter_by_date(Article.published.all(), year, month, day)
    data = { 'articles': articles, 'year': year, 'month': month, 'day': day }
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)


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


def subsection(request, section, subsection, year=None, month=None, day=None):
    data = {}
    data['section'] = sec = get_object_or_404(Section, slug=section)
    
    if subsection:
        sub = get_object_or_404(Subsection, section=sec, slug=subsection)
        data['subsection'] = sub
        
        try:
            column = sub.column
        except Column.DoesNotExist:
            pass
        else:
            data['column'] = column
            data['columns'] = Column.objects.order_by('-year', '-semester')
        
        base = filter_by_date(sub.articles, year, month, day)
    else:
        base = filter_by_date(sec.articles, year, month, day)
        data['columns'] = Column.objects.order_by('-year', '-semester')
    
    tops, mids, lows = Article.published.get_stories(base=base,
                                         num_top=2, num_mid=3, num_low=12)
    lowlist = [ [], [], [], [] ]
    for i in range(len(lows)):
        lowlist[i % 4].append(lows[i])
    
    data['topstories'] = tops
    data['midstories'] = mids
    data['lowlist'] = lowlist
    
    data['year'] = year
    data['month'] = month
    data['day'] = day
    
    if subsection:
        data['comments'] = PublicComment.visible.filter(
            article__subsections=sub
        ).order_by('-time')
        template = ("sections/sub_%s.html" % sub.slug,
                    "sections/sub_of_%s.html" % sec.slug,
                    "sections/subsection.html")
    else:
        data['comments'] = PublicComment.visible.filter(
            article__section=sec
        ).order_by('-time')
        template = ("sections/sec_%s.html" % sec.slug,
                    "sections/subsection.html")
    
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)

def section(request, section, year=None, month=None, day=None, template="section.html"):
    return subsection(request, section, None, year, month, day)


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
