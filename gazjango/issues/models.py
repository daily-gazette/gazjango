from django.db        import models
from django.db.models import permalink

from gazjango.articles.models      import Article
from gazjango.announcements.models import Announcement
from gazjango.athletics.models     import Team, Game

import datetime
from gazjango.scrapers import sharples
from gazjango.scrapers import weather
from gazjango.scrapers import events

def _combine_date_time(date, time=None):
    return datetime.datetime.combine(date, time or datetime.time(0))

class EventManager(models.Manager):
    def for_date(self, date, forward=datetime.timedelta(days=0)):
        "Returns the events for a certain day."
        start = date
        end = date + forward
        return self.filter(start_day__lte=end, end_day__gte=start)
    
    def update(self, forward=None, start=None):
        if not forward:
            forward = datetime.timedelta(days=7)
        if not start:
            start = datetime.date.today()
        
        existing = self.for_date(start, forward=forward)
        scraped = events.scrape_events_feed(start=start, end=start+forward)
        
        for event_dict in scraped:
            try:
                e = existing.get(link=event_dict['link'])
                e.start_day  = event_dict['start_day']
                e.start_time = event_dict['start_time']
                e.end_day    = event_dict['end_day']
                e.end_time   = event_dict['end_time']
                e.name     = event_dict['name']
                e.location = event_dict['location']
                e.sponsor  = event_dict['sponsor']
                e.save()
            except Event.DoesNotExist:
                Event.objects.create(**event_dict)
    

class Event(models.Model):
    "An event scraped from the College calendar."
    name = models.CharField(max_length=160)
    
    start_day = models.DateField()
    end_day   = models.DateField()
    
    start_time = models.TimeField(blank=True, null=True)
    end_time   = models.TimeField(blank=True, null=True)
    
    location = models.CharField(max_length=100, blank=True)
    sponsor  = models.CharField(max_length=100, blank=True)
    
    link = models.URLField(unique=True)
    
    objects = EventManager()
    
    def start(self):
        return _combine_date_time(self.start_day, self.start_time)
    
    def end(self):
        return _combine_date_time(self.end_day, self.end_time)
    
    def __unicode__(self):
        return "%s (%s - %s)" % (self.name, self.start(), self.end())
    
    def get_absolute_url(self):
        return self.link
    

ISSUE_CUTOFF_TIME = datetime.time(15, 0, 0)
class IssuesManager(models.Manager):
    def populate_issue(self, tomorrow=None):
        if tomorrow is None:
            tomorrow = datetime.datetime.now().time() > ISSUE_CUTOFF_TIME
        day = datetime.date.today() + datetime.timedelta(days=(1 if tomorrow else 0))
        
        issue, created = self.get_or_create(date=day)
        if not issue.menu:
            issue.menu = Menu.objects._for_today_or_tomorrow(tomorrow)
        if not issue.weather:
            issue.weather = Weather.objects._get_or_parse(tomorrow)
        if not issue.joke:
            try:
                issue.joke = WeatherJoke.objects.get(date=day)
            except WeatherJoke.DoesNotExist:
                issue.joke = WeatherJoke.objects.latest()
        if not issue.articles.count():
            last_issue = issue.get_previous_by_date()
            arts = Article.published.filter(pub_date__gte=last_issue.date, issues=None)
            issue.articles = arts
        
        issue.save()
        return (issue, created)
    

class IssuesWithArticlesManager(IssuesManager):
    def get_query_set(self):
        base = super(IssuesWithArticlesManager, self).get_query_set()
        return base.exclude(articles=None)
    

class Issue(models.Model):
    """
    An issue of the paper.
    
    Articles are ordered; the first one is the top story, and appears with 
    an image and a brief description. The next two are medium stories, with
    brief descriptions only; the remainder appear only as "More Stories".
    Note that although we use a many-to-many field for them, we use an
    intermediary 'through' model, with order_with_respect_to; to get them
    in order, you need to call articles_in_order().
    
    Announcements are fetched according to the date and cannot be ordered.
    I don't think this should be a problem....
    """
    
    articles = models.ManyToManyField(Article, related_name='issues')
    
    date    = models.DateField(default=datetime.date.today)
    menu    = models.ForeignKey('Menu', null=True)
    weather = models.ForeignKey('Weather', null=True)
    joke    = models.ForeignKey('WeatherJoke', null=True)
    
    objects = IssuesManager()
    with_articles = IssuesWithArticlesManager()
    
    def articles_in_order(self, racy=True):
        """
        Returns this issue's articles, in the order in which they should
        appear in the issue.
        """
        a = self.articles.order_by('position', 'possible_position', '-pub_date')
        return a if racy else a.filter(is_racy=False)
    
    def announcements(self):
        """Grabs the announcements that should appear in this issue."""
        a = Announcement.community
        return a.filter(date_start__lte=self.date, date_end__gte=self.date)
        
    def games(self):
        """Grabs the games that should appear in this issue."""
        g = Game.objects
        return g.filter(date__gte=self.get_previous_by_date().date, date__lt=self.date)
    
    def staff_announcement(self):
        """Gets the staff announcement for this issue, if any."""
        try:
            return Announcement.staff.get(date_start__lte=self.date, date_end__gte=self.date)
        except Announcement.DoesNotExist:
            return None
        except Announcement.MultipleObjectsReturned:
            # log this somehow
            return None
    
    def events(self):
        """Grabs the events that should appear in this issue."""
        events = Event.objects.for_date(self.date, forward=datetime.timedelta(days=2))
        return events.order_by('start_day', 'start_time')[:10]
    
    def topstory(self, racy=True):
        return self.articles_in_order(racy)[0]
    
    def midstories(self, racy=True, num=2):
        return self.articles_in_order(racy)[1:1+num]
    
    def lowstories(self, racy=True, skip=3):
        return self.articles_in_order(racy)[skip:]
    
    def __unicode__(self):
        return self.date.strftime("%a, %d %B %Y")
    
    class Meta:
        get_latest_by = 'date'
        ordering = ('-date',)
    
    @permalink
    def get_absolute_url(self):
        a = [str(x) for x in (self.date.year, self.date.month, self.date.day)]
        return ('issue', a)
    

class MenuManager(models.Manager):
    def for_today(self, ignore_cached=False):
        """
        Returns the Sharples menu object for today, creating a new
        one by scraping it from the XML feed if necessary.
        """
        return self._for_today_or_tomorrow(False, ignore_cached)
    
    def for_tomorrow(self, ignore_cached=False):
        """
        Returns the Sharples menu object for tomorrow, creating a new
        one by scraping it from the XML feed if necessary.
        """
        return self._for_today_or_tomorrow(True, ignore_cached)
    
    def _for_today_or_tomorrow(self, tomorrow, ignore_cached=False):
        date = datetime.date.today() + \
               datetime.timedelta(days=(1 if tomorrow else 0))
        try:
            menu = self.get(date=date)
            if not ignore_cached:
                return menu
        except self.model.DoesNotExist:
            menu = self.model()
        
        vals = self.scrape_menu(tomorrow, yield_dict=True)
        for key, val in vals.iteritems():
            menu.__setattr__(key, val)
        menu.save()
        return menu
    
    def scrape_menu(self, tomorrow=False, yield_dict=False):
        """
        Scrapes the XML feed for Sharples and returns a menu object for
        either today or tomorrow. Note that the menu is not saved.
        
        If `yield_dict` is passed, return a dictionary of values
        rather than an object.
        """
        menu = sharples.get_menu(tomorrow=tomorrow)
        
        return (dict if yield_dict else self.model)(
            date    = datetime.date.today() + 
                      datetime.timedelta(days=(1 if tomorrow else 0)),
            closed  = menu['closed'],
            message = menu['message'],
            lunch   = menu['lunch']  if 'lunch'  in menu else "",
            dinner  = menu['dinner'] if 'dinner' in menu else ""
        )
    

class Menu(models.Model):
    """The menu at Sharples for a given day."""
    
    date = models.DateField(default=datetime.date.today)
    
    closed  = models.BooleanField(default=False)
    message = models.TextField(blank=True)
    
    lunch  = models.TextField(blank=True)
    dinner = models.TextField(blank=True)
    
    objects = MenuManager()
    
    def __unicode__(self):
        return self.date.strftime("%m/%d/%Y")
    


class WeatherManager(models.Manager):
    def for_today(self, ignore_cached=False):
        """
        Returns the weather object for today, creating a new
        one (by parsing it from the online data feed) if necessary.
        """
        return self._get_or_parse(False, ignore_cached)
    
    def for_tomorrow(self, ignore_cached=False):
        """
        Returns the weather object for tomorrow, creating a new
        one (by parsing it from the online data feed) if necessary.
        """
        return self._get_or_parse(True, ignore_cached)
    
    def _get_or_parse(self, tomorrow=False, ignore_cached=False):
        day = datetime.date.today()
        if tomorrow:
            day += datetime.timedelta(days=1)
        
        try:
            obj = self.get(date=day)
            if not ignore_cached:
                return obj
        except self.model.DoesNotExist:
            obj = self.model()
        
        try:
            data = weather.get_weather(date=day)
        except weather.WeatherError:
            data = { 'today': "", 'tonight': "", 'tomorrow': "" }
        
        obj.date     = day
        obj.today    = data['today']
        obj.tonight  = data['tonight']
        obj.tomorrow = data['tomorrow']
        obj.save()
        
        return obj
    

class Weather(models.Model):
    """
    Weather published for a given day. Includes the forecast for the day in
    question, that day's night, and the next day.
    
    Note that this is not necessarily connected with an issue; it is updated
    daily, so that over weekends / breaks it doesn't become totally irrelevant.
    Days where we don't publish will still have a Weather object.
    """
    
    date = models.DateField(default=datetime.date.today)
    
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
    
    date = models.DateField(default=datetime.date.today)
    
    line_one   = models.CharField(max_length=100)
    line_two   = models.CharField(max_length=100)
    line_three = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.date.strftime("%m/%d/%Y")
    
    class Meta:
        get_latest_by = "date"
    
