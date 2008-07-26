from django.template  import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from articles.models      import Article, Special
from announcements.models import Announcement
from comments.models      import PublicComment
from issues.models        import Menu, Weather, WeatherJoke
from jobs.models          import JobListing
from datetime import date, timedelta

def article(request, slug, year, month, day, template="story.html"):
    story = get_object_or_404(Article, slug=slug,
                pub_date__year=year, pub_date__month=month, pub_date__day=day)
    data = {
        'story': story,
        'related': story.related_list(3),
        'topstory': Article.published.get_top_story(),
        'comments': []
    }
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)

def articles(request, year=None, month=None, day=None):
    articles = Article.published_objects.all()
    if year:
        articles = articles.filter(pub_date__year=year)
        if month:
            articles = articles.filter(pub_date__month=month)
            if day:
                articles = articles.filter(pub_date__day=day)
    to_return = ""
    for article in articles:
        to_return += article.slug + "\n"
    from django.http import HttpResponse
    return HttpResponse(to_return)


def homepage(request, template="index.html"):
    data = {
        'topstory': Article.published.get_top_story(),
        'midstories': Article.published.get_secondary_stories(2),
        'lowstories': Article.published.get_tertiary_stories(6),
        
        'comments': PublicComment.visible.order_by('-time').all()[:5],
        'weather': Weather.objects.for_today(),
        'joke': WeatherJoke.objects.latest(),
        
        'specials': Special.objects.order_by('-date').all()[:10],
        'announcements': Announcement.community.now_running(),
        'jobs': JobListing.objects.filter(is_filled=False)[:3],
        
        'tomorrow': date.today() + timedelta(days=1)
    }
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)


def menu_partial(request):
    menu = Menu.objects.for_today()
    return render_to_response("scraped/menu.html", { 'menu': menu })

search        = lambda request, **kwargs: render_to_response("base.html", locals())
comment       = lambda request, **kwargs: render_to_response("base.html", locals())
print_article = lambda request, **kwargs: render_to_response("base.html", locals())
email_article = lambda request, **kwargs: render_to_response("base.html", locals())
archives      = articles

category           = lambda request, **kwargs: render_to_response("base.html", locals())
category_for_year  = lambda request, **kwargs: render_to_response("base.html", locals())
category_for_month = lambda request, **kwargs: render_to_response("base.html", locals())
category_for_day   = lambda request, **kwargs: render_to_response("base.html", locals())
