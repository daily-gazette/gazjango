import datetime

from django.template   import RequestContext
from django.shortcuts  import render_to_response, get_object_or_404
from misc.view_helpers import get_by_date_or_404, filter_by_date

from articles.models      import Article, Section, Subsection, Special, PhotoSpread
from announcements.models import Announcement
from comments.models      import PublicComment
from comments.forms       import AnonCommentForm, UserCommentForm
from issues.models        import Menu, Weather, WeatherJoke
from jobs.models          import JobListing

from scrapers.bico         import get_bico_news
from scrapers.tla          import get_tla_links
from scrapers.manual_links import manual_links, lca_links


def article(request, slug, year, month, day, print_view=False, template="stories/view.html"):
    story = get_by_date_or_404(Article, year, month, day, slug=slug)
    
    initial = {'text': 'Have your say.'}
    if request.user.is_authenticated():
        initial['name'] = request.user.name
        form = UserCommentForm(inital=initial)
    else:
        form = AnonCommentForm(initial=initial)
    
    data = {
        'story': story,
        'related': story.related_list(3),
        'topstory': Article.published.get_top_story(),
        'comments': story.comments.all().order_by('time'),
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
    top, mids, lows = Article.published.get_stories(num_mids=2, num_lows=6)
    data = {
        'topstory': top,
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


def menu_partial(request):
    if datetime.datetime.hour() < 21:
        menu = Menu.objects.for_today()
    else:
        menu = Menu.objects.for_tomorrow()
    return render_to_response("scraped/menu.html", { 'menu': menu })


def spread(request, slug, year, month, day, num=None):
    spread = get_by_date_or_404(PhotoSpread, year, month, day, slug=slug)
    data = {'spread': spread}
    if num:
        data['page'] = spread.get_photo_number(num)
    rc = RequestContext(request)
    return render_to_response("photo_spread.html", data, context_instance=rc)


search        = lambda request, **kwargs: render_to_response("base.html", locals())
comment       = lambda request, **kwargs: render_to_response("base.html", locals())
email_article = lambda request, **kwargs: render_to_response("base.html", locals())

def section(request, section, year=None, month=None, day=None, template="section.html"):
    sec = get_object_or_404(Section, slug=section)
    data = {
        'section': sec,
        'articles': filter_by_date(section.articles, year, month, day),
        'year': year,
        'month': month,
        'day': day
    }
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)

def subsection(request, section, subsection, year=None, month=None, day=None, template="subsection.html"):
    sec = get_object_or_404(Section, slug=section)
    sub = get_object_or_404(Subsection, section=sec, slug=subsection)
    data = {
        'section': sec,
        'subsection': sub,
        'articles': filter_by_date(sub.articles, year, month, day),
        'year': year,
        'month': month,
        'day': day
    }
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)