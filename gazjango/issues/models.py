from django.db        import models
from django.db.models import permalink

from articles.models      import Article
from announcements.models import Announcement

from datetime import date, timedelta
import scrapers.sharples
import scrapers.weather


class Issue(models.Model):
    """An issue of the paper."""
    
    articles = models.ManyToManyField(Article,
                                      through='IssueArticle', 
                                      related_name='issues')
    announcements = models.ManyToManyField(Announcement, 
                                           through='IssueAnnouncement',
                                           related_name='issues')
    
    date    = models.DateField(default=date.today)
    menu    = models.ForeignKey('Menu', null=True)
    weather = models.ForeignKey('Weather', null=True)
    joke    = models.ForeignKey('WeatherJoke', null=True)
    events  = models.TextField(blank=True)
    
    def articles_in_order(self):
        """
        Returns the articles in the order in which they should appear in the issue.
        """
        return self.articles.order_by('issuearticle___order')
    
    def add_article(self, article):
        "Appends an article to this issue."
        IssueArticle.objects.create(issue=self, article=article)
    
    def add_announcement(self, announcement):
        "Appends an announcement to this issue."
        IssueAnnouncement.objects.create(issue=self, announcement=announcement)
    
    def __unicode__(self):
        return self.date.strftime("%a, %d %B %Y")
    
    @permalink
    def get_absolute_url(self):
        a = [str(x) for x in (self.date.year, self.date.month, self.date.day)]
        return ('issues.views.for_date', a)
    

class IssueArticle(models.Model):
    "An issue's having an article. Includes position metadata."
    
    issue    = models.ForeignKey(Issue)
    article  = models.ForeignKey(Article)
    
    class Meta:
        order_with_respect_to = 'issue'
        unique_together = ('issue', 'article')
    
    def __unicode__(self):
        return u"%s on %s" % (self.article.slug, self.issue.date)
    

class IssueAnnouncement(models.Model):
    "An issue's having an announcement. Includes position metadata."
    
    issue        = models.ForeignKey(Issue)
    announcement = models.ForeignKey(Announcement)
    
    class Meta:
        order_with_respect_to = 'issue'
        unique_together = ('issue', 'announcement')
    
    def __unicode__(self):
        return u"%s on %s" % (self.announcement.slug, self.issue.date)
    

class MenuManager(models.Manager):
    def for_today(self):
        return self.get_or_parse(tomorrow=False)
    
    def for_tomorrow(self):
        return self.get_or_parse(tomorrow=True)
    
    def get_or_parse(self, tomorrow=False):
        """
        Returns the Sharples menu object for today/tomorrow, creating a
        new one (by parsing it from the XML feed) if necessary.
        """
        day = date.today()
        if tomorrow:
            day += timedelta(days=1)
        
        try:
            return self.get(date=day)
        
        except self.model.DoesNotExist:
            menu = scrapers.sharples.get_menu(tomorrow=tomorrow)
            return self.create(
                date    = day,
                closed  = menu['closed'],
                message = menu['message'],
                lunch   = menu['lunch'],
                dinner  = menu['dinner']
            )
    

class Menu(models.Model):
    """The menu at Sharples for a given day."""
    
    date = models.DateField(default=date.today)
    
    closed  = models.BooleanField(default=False)
    message = models.TextField(blank=True)
    
    lunch  = models.TextField(blank=True)
    dinner = models.TextField(blank=True)
    
    objects = MenuManager()
    
    def __unicode__(self):
        return self.date.strftime("%m/%d/%Y")
    


class WeatherManager(models.Manager):
    def for_today(self):
        return self.get_or_parse(tomorrow=False)
    
    def for_tomorrow(self):
        return self.get_or_parse(tomorrow=True)
    
    def get_or_parse(self, tomorrow=False):
        """
        Returns the weather object for today/tomorrow, creating a new
        one (by parsing it from the online data feed) if necessary.
        """
        day = date.today()
        if tomorrow:
            day += timedelta(days=1)
        try:
            return self.get(date=day)
        
        except self.model.DoesNotExist:
            weather = scrapers.weather.get_weather(date=day)
            return self.create(
                date     = day,
                today    = weather['today'],
                tonight  = weather['tonight'],
                tomorrow = weather['tomorrow']
            )
    

class Weather(models.Model):
    """
    Weather published for a given day. Includes the forecast for the day in
    question, that day's night, and the next day.
    
    Note that this is not necessarily connected with an issue; it is updated
    daily, so that over weekends / breaks it doesn't become totally irrelevant.
    Days where we don't publish will still have a Weather object.
    """
    
    date = models.DateField(default=date.today)
    
    today    = models.CharField(max_length=100)
    tonight  = models.CharField(max_length=100)
    tomorrow = models.CharField(max_length=100)
    
    objects = WeatherManager()
    
    def __unicode__(self):
        return self.date.strftime("%m/%d/%Y")
    

class WeatherJoke(models.Model):
    """
    The weather joke. A long-time tradition that most of those who send
    out (except Urooj) have always wanted to abolish, and yet it's a 
    Gazette tradition that *someone* complains about when we quietly try
    to forget about it. Persistent little bastard.
    """
    
    date = models.DateField(default=date.today)
    
    line_one   = models.CharField(max_length=100)
    line_two   = models.CharField(max_length=100)
    line_three = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.date.strftime("%m/%d/%Y")
    
    class Meta:
        get_latest_by = "date"
    
