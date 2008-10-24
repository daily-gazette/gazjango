from django.db import models
from django.contrib.sites.models import Site
from gazjango.articles.models import Format
from gazjango.articles import formats

class Page(models.Model):
    "A very slight extension of django.contrib.flatpages."
    
    url    = models.CharField('URL', max_length=100, db_index=True)
    title  = models.CharField('title', max_length=200)
    parent = models.ForeignKey('self', null=True, blank=True)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    content = models.TextField('content', blank=True)
    format = models.ForeignKey(Format)
    template_name = models.CharField('template name', max_length=70, blank=True,
        help_text="Example: 'flatpages/contact_page.html'. If this isn't provided, the system will use 'flatpages/default.html'.")
    sites = models.ManyToManyField(Site)
    
    class Meta:
        verbose_name = 'stacked page'
        verbose_name_plural = 'stacked pages'
        ordering = ('url',)
    
    def __unicode__(self):
        return u"%s -- %s" % (self.url, self.title)
    
    def get_absolute_url(self):
        return self.url
    
    def formatted_content(self):
        formatter = getattr(formats, self.format.function)
        return formatter(self.content)
    
    def ancestors(self):
        """
        Returns a list of this page's parent, their parents, through to 
        the current page.
        
          [grandparent, parent, self]
        """
        lst = [self]
        curr = self
        while curr.parent:
            curr = curr.parent
            lst.insert(0, curr)
        return lst
    
