from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.syndication.feeds import Feed, FeedDoesNotExist
from django.utils import feedgenerator
from gazjango.misc.helpers import flatten

from collections                    import defaultdict

from django.conf                    import settings
from django.db.models               import Q
from django.http                    import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts               import render_to_response
from django.template                import RequestContext
from django.utils.html              import escape

from gazjango.articles.models      import Article
from gazjango.articles.views       import specific_article
from gazjango.comments.forms       import make_comment_form
from gazjango.comments.models      import PublicComment, CommentIsSpam
from gazjango.misc                 import recaptcha
from gazjango.misc.view_helpers    import get_ip, get_user_profile, is_robot
from gazjango.misc.view_helpers    import get_by_date_or_404, boolean_arg

class CommentFeed(Feed):
    title_template = 'feeds/story_headline.html'
    description_template = 'feeds/story_summary.html'
    
    def item_author_name(self, item):
        return item.authors.all()[0].name
    
    def item_author_link(self, item):
        dom = Site.objects.get_current().domain
        url = item.authors.all()[0].get_absolute_url()
        return "http://%s/%s" % (dom, url)
    
    def item_pubdate(self, item):
        return item.pub_date
    
    def item_categories(self, item):
        sec = [item.section.name]
        sub = [item.subsection.name] if item.subsection else []
        # tags = [tag.name for tag in item.tags.all()]
        return sec + sub # + tags
        
    link = '/'
    title = 'The Daily Gazette'
    description = 'The latest coments from the Daily Gazette.'

    def items(self):
        stories = Article.published.get_stories(num_top=1, num_mid=2, num_low=7)
        return flatten(stories)
    

class MainFeed(StoryFeed):
    link = '/'
    title = 'The Daily Gazette'
    description = 'The latest news from the Daily Gazette.'
    
    def items(self):
        stories = Article.published.get_stories(num_top=1, num_mid=2, num_low=7)
        return flatten(stories)

