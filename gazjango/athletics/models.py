from django.db import models
from django.contrib.sites.models import Site
from gazjango.media.models import ImageFile
import datetime

class Team(models.Model):
    "Represents a Swat sports team."
    slug = models.SlugField()
    sport = models.CharField('sport', max_length=100, blank=True)
    
    GENDER_CHOICES = (
        ('m',"Men's"),
        ('w',"Women's"),
        ('b',""),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    
    TRIMESTER_CHOICES = (
        ('1','Spring'),
        ('2','Winter'),
        ('3','Fall'),
    )
    trimester = models.CharField(max_length=1, choices=TRIMESTER_CHOICES)
    
    coaches = models.CharField('coaches', max_length=100, blank=True)
    members = models.TextField('members', blank=True)
    
    club = models.BooleanField(default=False)
    icon = models.ForeignKey(ImageFile,related_name="teams_with_icon")
    ranked = models.BooleanField(default=False)
    
    def full_team_name(self):
        if self.gender == 'b':
            return self.sport
        else:
            return "%s %s" % (self.get_gender_display(), self.sport)
    
    def scores(self,all_time=False):
        base = self.games_for_trimester(all_time)
        return [
            base.filter(outcome='w').count(),
            base.filter(outcome='l').count(),
            base.filter(outcome='d').count()
        ]
    
    def all_time_scores(self):
        return self.scores(True)
    
    def games_for_trimester(self, all_time=False, year=None):
        if all_time:
            return self.games
        else:
            today = datetime.date.today()
            year = year or today.year
            start_year = year if today.month >= 8 else year - 1
            return self.games.filter(date__gt=datetime.date(year, 8, 1))
    
    def most_recent_game(self):
        return self.games.latest()
    
    @models.permalink   
    def get_absolute_url(self):
        return ('athletics_team', [self.slug])
    
    def __unicode__(self):
        return self.full_team_name()

class Game(models.Model):
    "Represents a specific game."
    date = models.DateField(default=datetime.date.today)
    
    home = models.BooleanField(default=False, blank=True)
    in_conference = models.BooleanField(default=True, blank=True)
    
    team = models.ForeignKey(Team, related_name="games")
    opponent = models.CharField(max_length=100, blank=True)
    
    game_notes = models.TextField(blank=True)
    link_list = models.TextField(blank=True)
    
    OUTCOME_CHOICES = (
        ('w','Win'),
        ('l','Lost'),
        ('d','Draw'),
        ('p','Postponed'),
    )
    outcome = models.CharField(max_length=1,choices=OUTCOME_CHOICES,blank=True)
    
    # for normal games
    swat_score = models.IntegerField(blank=True, null=True)
    opponent_score = models.IntegerField(blank=True, null=True)
    
    rank = models.IntegerField(blank=True, null=True,
            help_text="Rank in a competition -- for cross-country or the like.")
    
    class Meta:
        get_latest_by = "date"
        ordering = ("-date", "team")
    
    def __unicode__(self):
        return "%s vs %s on %s" % (self.team.full_team_name(), 
                                   self.opponent, 
                                   self.date.strftime("%Y-%m-%d"))
    
