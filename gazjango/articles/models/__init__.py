from articles   import Article, ArticleRevision, Format
from categories import Category
from specials   import Special, SpecialsCategory
from concepts   import StoryConcept
import tagging

try:
    tagging.register(Article)
except tagging.AlreadyRegistered:
    pass

Category.all_articles = lambda self: \
    Article.objects.filter(category__in=[d.pk for d in self.descendants()])
