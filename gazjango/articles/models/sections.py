from django.db import models
from stories   import Article

class Section(models.Model):
    """
    A section of coverage: news, features, opinions, columns....
    
    Each article belongs to exactly one section, and any number
    of subsections within that section.
    """
    
    name = models.CharField(max_length=40, unique=True)
    slug = models.SlugField(unique=True)
    description = models.CharField(max_length=250, blank=True)
    is_special = models.BooleanField(blank=True, default=False,
                   help_text="Whether articles in this section will have " \
                              "the section name on the homepage.")
    
    class Meta:
        app_label = 'articles'
    
    def __unicode__(self):
        return self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ('section', [self.slug])
    
    def get_stories(self, num_top=2, num_mid=3, num_low=12, **extra):
        "Calls Article.published.get_stories for stories in this section."
        return Article.published.get_stories(
            base = self.articles,
            num_top = num_top,
            num_mid = num_mid,
            num_low = num_low
        )
    

class Subsection(models.Model):
    """
    A subsection: Ask the Gazette, College News, a specific column, whatever.
    
    If `is_over` is set, don't have it show up in the list in the admin. Used
    mainly for columns that are no longer running. There's nothing app-level
    that actually prevents new articles using it, however.
    """
    
    name = models.CharField(max_length=40)
    slug = models.SlugField(unique=True)
    description = models.CharField(max_length=250, blank=True)
    section = models.ForeignKey(Section, related_name="subsections")
    
    # these are really only used for columns
    # TODO: maybe we should separate columns into a subclass of Subsection?
    authors = models.ManyToManyField('accounts.UserProfile')
    big_logo   = models.ForeignKey('media.ImageFile', null=True, blank=True, related_name="subsections_with_big_logo")
    small_logo = models.ForeignKey('media.ImageFile', null=True, blank=True, related_name="subsections_with_small_logo")
    is_over = models.BooleanField(default=False)
    
    class Meta:
        app_label = 'articles'
    
    def __unicode__(self):
        return self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ('subsection', [self.section.slug, self.slug])
    
    def get_stories(self, num_top=2, num_mid=3, num_low=12):
        "Calls Articles.published.get_stories for stories in this subsection."
        return Articles.published.get_stories(
            base = self.articles,
            num_top = num_top,
            num_mid = num_mid, 
            num_low = num_low
        )
    
