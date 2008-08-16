import datetime

from django.contrib.auth.decorators import permission_required
from django.template   import RequestContext
from django.shortcuts  import render_to_response, get_object_or_404
from django.http       import Http404, HttpResponse, HttpResponseRedirect
from django.utils.html import escape
from misc.view_helpers import get_by_date_or_404, filter_by_date, reporter_admin_data

from articles.models      import Article, Section, Subsection, Special, PhotoSpread
from articles.models      import StoryConcept
from announcements.models import Announcement
from comments.models      import PublicComment
from comments.forms       import CommentForm, make_comment_form
from issues.models        import Weather, WeatherJoke
from jobs.models          import JobListing
from tagging.models       import TagGroup, Tag

from scrapers.bico         import get_bico_news
from scrapers.tla          import get_tla_links
from scrapers.manual_links import manual_links, lca_links


def article(request, slug, year, month, day, print_view=False, template="stories/view.html"):
    story = get_by_date_or_404(Article, year, month, day, slug=slug)    
    logged_in = request.user.is_authenticated()
    
    if request.method != 'POST':
        initial = {'text': 'Have your say.'}
        if logged_in:
            initial['name'] = request.user.get_full_name()
        form = make_comment_form(logged_in=logged_in, initial=initial)
        
        return show_article(request, story, form, print_view, template)
    
    else:
        form = make_comment_form(data=request.POST, logged_in=logged_in)
        
        if form.is_valid():
            args = {
                'subject': story,
                'text': escape(form.cleaned_data['text']).replace("\n", "<br/>"),
                'ip_address': request.META['REMOTE_ADDR'],
                'user_agent': request.META['HTTP_USER_AGENT']
            }
            
            if logged_in:
                args['user'] = request.user.get_profile()
            if form.cleaned_data['anonymous']:
                args['name']  = form.cleaned_data['name']
                args['email'] = form.cleaned_data['email']
            
            comment = PublicComment.objects.new(**args)
            return HttpResponseRedirect(comment.get_absolute_url())
        else:
            return show_article(request, story, form)


def show_article(request, story, form, print_view=False, extra={}, template="stories/view.html"):
    data = {
        'story': story,
        'related': story.related_list(3),
        'topstory': Article.published.get_top_story(),
        'comments': story.comments.order_by('-time').exclude(article=story),
        'print_view': print_view,
        'comment_form': form
    }
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)


def articles(request, year=None, month=None, day=None, template="article_list.html"):
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
        
        'comments': PublicComment.visible.order_by('-time').all()[:4],
        'weather': Weather.objects.for_today(),
        'joke': WeatherJoke.objects.latest(),
        
        'specials': Special.objects.order_by('-date').all()[:10],
        'announcements': Announcement.community.now_running(),
        'jobs': JobListing.objects.order_by('-pub_date').filter(is_filled=False)[:3],
        
        'bico_news': get_bico_news(),
        'tla_links': get_tla_links(),
        'manual_links': manual_links,
        'lca_links': lca_links
    }
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)


def spread(request, slug, year, month, day, num=None):
    spread = get_by_date_or_404(PhotoSpread, year, month, day, slug=slug)
    data = {'spread': spread}
    if num:
        data['page'] = spread.get_photo_number(num)
    rc = RequestContext(request)
    return render_to_response("photo_spread.html", data, context_instance=rc)

search        = lambda request, **kwargs: render_to_response("base.html", locals())
email_article = lambda request, **kwargs: render_to_response("base.html", locals())


def subsection(request, section, subsection, year=None, month=None, day=None, template="subsection.html"):
    data = {}
    data['section'] = sec = get_object_or_404(Section, slug=section)
    
    if subsection:
        sub = get_object_or_404(Subsection, section=sec, slug=subsection)
        data['subsection'] = sub
        base = filter_by_date(sub.articles, year, month, day)
    else:
        base = filter_by_date(sec.articles, year, month, day)
    
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
    else:
        data['comments'] = PublicComment.visible.filter(
            article__section=sec
        ).order_by('-time')
    
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)

def section(request, section, year=None, month=None, day=None, template="section.html"):
    return subsection(request, section, None, year, month, day, template)


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
