import datetime

from django.template   import RequestContext
from django.shortcuts  import render_to_response, get_object_or_404
from django.http       import Http404, HttpResponse, HttpResponseRedirect
from misc.view_helpers import get_by_date_or_404, filter_by_date

from articles.models      import Article, Section, Subsection, Special, PhotoSpread
from announcements.models import Announcement
from comments.models      import PublicComment
from comments.forms       import CommentForm, make_comment_form
from issues.models        import Menu, Weather, WeatherJoke
from jobs.models          import JobListing

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
        print request.POST
        form = make_comment_form(data=request.POST, logged_in=logged_in)
        if form.is_valid():
            args = {
                'subject': story,
                'text': form.cleaned_data['text'].replace("\n", "<br/>"),
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


def get_comment_text(request, slug, year, month, day, num):
    story = get_by_date_or_404(Article, year, month, day, slug=slug)
    try:
        comment = story.comments.get(number=num)
        return HttpResponse(comment.text)
    except PublicComment.DoesNotExist:
        raise Http404

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


def menu_partial(request):
    if datetime.datetime.now().hour < 21:
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
