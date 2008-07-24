from django.db        import models
from django.db.models import permalink

class Category(models.Model):
    """
    A category of articles: news, features, etc.
    
    Sub-categories are supported and should generally be used. For example,
    you could have News >> Students, or Columns >> Honors Denglish.
    """
    
    name        = models.CharField(max_length=40, unique=True)
    description = models.CharField(blank=True, max_length=250)
    slug        = models.SlugField(unique=True)
    parent      = models.ForeignKey('self',
                                    blank=True,
                                    null=True,
                                    related_name='children')
    
    def ancestors(self):
        """Returns all super-categories of this category, including itself.
        
        Ordering is [grandparent, parent, self]."""
        curr = self
        ancestors = [self]
        while curr.parent is not None:
            ancestors.insert(0, curr.parent)
            curr = curr.parent
        return ancestors
    
    def root(self):
        """Returns the highest super-category of this category."""
        curr = self
        while curr.parent is not None:
            curr = curr.parent
        return curr
    
    def descendants(self):
        """Returns all sub-categories of this category, including itself.
        
        This is a preorder / depth-first traversal, so the ordering is
        [self, child1, grandchild1a, grandchild1b, child2, grandchild2a],
        if that makes sense."""
        descendants = [self]
        for child in self.children.all():
            descendants.extend(child.descendants())
        return descendants
    
    def all_articles(self):
        "Returns all articles in this category or one of its sub-categories."
        # this is actually defined in __init__.py, because of import issues
        return None
    
    def __unicode__(self):
        return self.name
    
    @permalink
    def get_absolute_url(self):
        return ('articles.views.category', [self.slug])
    
    class Meta:
        app_label = 'articles'
    
