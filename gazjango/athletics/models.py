from django.db import models
from django.contrib.sites.models import Site
from gazjango.media.models import ImageFile
import datetime

class Team(models.Model):
     " The base class for the athletics section, which is an off shoot of the articles model "
     
     slug = models.SlugField()
     
     sport = models.CharField('sport', max_length=100, blank=True)
     
     GENDER_CHOICES = (
          ('m',"Men's"),
          ('w',"Women's"),
          ('b',""),
     )
     
     gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
     coaches = models.CharField('coaches', max_length=100, blank=True)
     members = models.TextField('members', blank=True)
     
     club = models.BooleanField(default=False)
     
     
     TRIMESTER_CHOICES = (
          ('1','Spring'),
          ('2','Winter'),
          ('3','Fall'),
     )
     
     trimester = models.CharField(max_length=1, choices=TRIMESTER_CHOICES)     
     
     ranked = models.BooleanField(default=False)
     
     icon = models.ForeignKey(ImageFile,related_name="teams_with_icon")
     
     def scores(self,all_time=False):
     
          base = self.games_for_trimester(all_time)
          
          return [
               base.filter(outcome='W').count(),
               base.filter(outcome='L').count(),
               base.filter(outcome='D').count()
          ]
          
     def all_time_scores(self):
        return self.scores(True)
        
     def 
          
     def games_for_trimester(self,all_time=False,year=None):
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
          
     
class Game(models.Model):
     " The class for any specific game "
     
     home = models.BooleanField(default=False,blank=True)
     in_conference = models.BooleanField(default=True,blank=True)
     
     team = models.ForeignKey(Team,related_name="games")
     opponent = models.CharField('opponent', max_length=100, blank=True)
     game_notes = models.TextField('game_notes', blank=True)
     link_list = models.TextField('link_list', blank=True)
     
     date = models.DateField(default=datetime.date.today)

     
     " for normal games "
     swat_score = models.IntegerField('swat_score', blank=True, null=True)
     opponent_score = models.IntegerField('opponent_score', blank=True, null=True)
     
     OUTCOME_CHOICES = (
          ('w','Win'),
          ('l','Lost'),
          ('d','Draw'),
          ('p','Postponed'),
     )
     
     outcome = models.CharField(max_length=1,choices=OUTCOME_CHOICES,blank=True)
     
     
     " rank in a competition for x-country or the like "
     rank = models.IntegerField('rank', blank=True, null=True)
     
     class Meta:
          get_latest_by = "date"