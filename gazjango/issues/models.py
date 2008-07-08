from django.db        import models
from django.db.models import permalink
from articles.models  import Article, Announcement
from datetime         import date

class Issue(models.Model):
    """An issue of the paper."""
    
    date    = models.DateField(default=date.today)
    menu    = models.TextField(blank=True)
    weather = models.TextField(blank=True)
    events  = models.TextField(blank=True)
    
    def add_article(self, article):
        """Appends an article to this issue."""
        IssueArticle.objects.create(issue=self, article=article)
    
    def add_announcement(self, announcement):
        """Appends an announcement to this issue."""
        IssueAnnouncement.objects.create(issue=self, announcement=announcement)
    
    def __unicode__(self):
        return self.date.strftime("%a, %d %B %Y")
    
    @permalink
    def get_absolute_url(self):
        a = [str(x) for x in (self.date.year, self.date.month, self.date.day)]
        return ('issues.views.for_date', a)
    

class IssueArticle(models.Model):
    """An issue's having an article. Includes position metadata."""
    
    issue    = models.ForeignKey(Issue, related_name="articles")
    article  = models.ForeignKey(Article, related_name="issues")
    
    class Meta:
        order_with_respect_to = 'issue'
        unique_together = ('issue', 'article')
    
    def __unicode__(self):
        return u"%s on %s" % (self.article.slug, self.issue.date)
    

class IssueAnnouncement(models.Model):
    """An issue's having an announcement. Includes position metadata."""
    
    issue        = models.ForeignKey(Issue, related_name="announcements")
    announcement = models.ForeignKey(Announcement, related_name="issues")
    
    class Meta:
        order_with_respect_to = 'issue'
        unique_together = ('issue', 'announcement')
    
    def __unicode__(self):
        return u"%s on %s" % (self.announcement.slug, self.issue.date)
    

