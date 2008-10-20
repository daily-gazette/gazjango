from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.syndication.feeds import Feed, FeedDoesNotExist
from django.utils import feedgenerator
from gazjango.misc.helpers import flatten

from gazjango.articles.models import Article, Section

class StoryFeed(Feed):
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
        tags = [tag.name for tag in item.tags.all()]
        return sec + sub + tags
    

class MainFeed(StoryFeed):
    link = '/'
    title = 'The Daily Gazette'
    description = 'The latest news from the Daily Gazette.'
    
    def items(self):
        stories = Article.published.get_stories(num_top=1, num_mid=2, num_low=7)
        return flatten(stories)
    

class TameFeed(MainFeed):
    def items(self):
        stories = Article.published.get_stories(num_top=1, num_mid=2, num_low=7,
                                base=Article.published.filter(is_racy=False))
        return flatten(stories)
    

class LatestStoriesFeed(MainFeed):
    title = 'The Daily Gazette :: Latest Stories'
    
    def items(self):
        return Article.published.order_by('-pub_date')[:10]
    


class SectionFeed(StoryFeed):
    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return Section.objects.get(slug=bits[0])
    
    def title(self, obj):
        return "The Daily Gazette :: %s" % obj.name
    
    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()
    
    def description(self, obj):
        return "Articles from the %s section." % obj.name
    
    def items(self, obj):
        return flatten(obj.get_stories(num_top=1, num_mid=2, num_low=7))
    

class SectionLatestFeed(SectionFeed):
    def title(self, obj):
        return super(SectionLatestFeed, self).title(obj) + " :: Latest Stories"
    
    def description(self, obj):
        return "The latest articles from the %s section." % obj.name
    
    def items(self, obj):
        return obj.articles.order_by('-pub_date')[:10]
    
