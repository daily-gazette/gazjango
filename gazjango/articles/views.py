from django.template  import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from articles.models      import Article
from announcements.models import Announcement
from comments.models      import PublicComment

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


def homepage(request, template="index.html"):
    data = {
        'topstory': Article.published.get_top_story(),
        'midstories': Article.published.get_secondary_stories(2),
        'lowstories': Article.published.get_tertiary_stories(6),
        'comments': PublicComment.visible.order_by('-time').all()[:5],
        'announcements': Announcement.community.now_running()
    }
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)


search        = lambda request, **kwargs: render_to_response("base.html", locals())
comment       = lambda request, **kwargs: render_to_response("base.html", locals())
print_article = lambda request, **kwargs: render_to_response("base.html", locals())
email_article = lambda request, **kwargs: render_to_response("base.html", locals())
archives      = lambda request, **kwargs: render_to_response("base.html", locals())

articles_for_year  = lambda request, **kwargs: render_to_response("base.html", locals())
articles_for_month = lambda request, **kwargs: render_to_response("base.html", locals())
articles_for_day   = lambda request, **kwargs: render_to_response("base.html", locals())

category           = lambda request, **kwargs: render_to_response("base.html", locals())
category_for_year  = lambda request, **kwargs: render_to_response("base.html", locals())
category_for_month = lambda request, **kwargs: render_to_response("base.html", locals())
category_for_day   = lambda request, **kwargs: render_to_response("base.html", locals())
