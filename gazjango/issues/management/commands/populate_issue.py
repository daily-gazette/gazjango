from django.core.management.base import NoArgsCommand
from gazjango.articles.models import Article
from gazjango.issues.models import Issue, Weather, Menu, WeatherJoke
import datetime

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        Issue.objects.populate_issue()
    
