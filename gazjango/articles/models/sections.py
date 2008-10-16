from django.db import models
from gazjango.articles.models.stories import Article
import datetime
import os.path
import settings

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
    
    def most_recent_article(self):
        "Returns the most recent story from this subsection."
        try:
            return self.articles.order_by('-pub_date')[0]
        except IndexError:
            return None
    
    def most_recent_articles(self, num=None):
        articles = self.articles.order_by('-pub_date')
        return articles[:num] if num else articles
    

class Column(Subsection):
    """
    A column. Adds some extra information.
    
    This should really be in the Columns category, but we're not hardcoding
    that in any way.
    """
    authors = models.ManyToManyField('accounts.UserProfile')
    is_over = models.BooleanField(default=False)
    
    SEMESTER_CHOICES = (
        ('1', 'Spring'),
        ('2', 'Fall'),
    )
    semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES)
    year = models.IntegerField(blank=True, default=lambda:datetime.date.today().year)
    
    class Meta:
        app_label = 'articles'
    
    def wide_logo_url(self):
        path = '/static/images/column/%s_wide.png' % self.slug
        return path if os.path.exists(settings.BASE + path) else None
    
    def square_logo_url(self):
        path = '/static/images/column/%s_square.png' % self.slug
        return path if os.path.exists(settings.BASE + path) else None
    

