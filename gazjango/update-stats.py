import sys
import optparse
import datetime
from googleanalytics import Connection

from django.core.management import setup_environ
from django.core.management import execute_manager
import settings

setup_environ(settings)

from gazjango.popular.models          import StoryRank
from gazjango.articles.models.stories import Article

# should be moved to settings when everything works
username = 'arador@gmail.com'
password = 'YOURS'
account  = '12436739'

connection = Connection(username,password)
account = connection.get_account(account)

end_date    = datetime.date.today()
start_date  = datetime.date.today() - datetime.timedelta(days = 60)

results = account.get_data(start_date=start_date,end_date=end_date,dimensions=['pagepath',],metrics=['pageviews',])
results = results.list

for item in results:
    path      = item[0][0]
    pageviews = item[1][0]
    url_list = path.split('/')
    if len(url_list) == 6:        
        year  = url_list[1]
        month = url_list[2]
        day   = url_list[3]
        slug  = url_list[4] 
        try:
            story = Article.objects.get(slug = slug)
            storyrank = StoryRank.objects.get_or_create(hits = int(pageviews),last_update = datetime.datetime.now(),article = story)
        except:
            pass
    else:
        pass
        
print "Done with the import."