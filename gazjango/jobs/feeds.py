from django.contrib.syndication.feeds import Feed, FeedDoesNotExist
from gazjango.jobs.models import JobListing

class JobsFeed(Feed):
    title_template = 'feeds/job_title.html'
    description_template = 'feeds/job_description.html'
    title = 'The Daily Gazette :: Jobs'
    link = '/jobs/'
    
    description = "Job listings from the Daily Gazette."
    
    def items(self):
        return JobListing.unfilled.order_by('-pub_date')[:10]
    
    def item_pubdate(self, item):
        return item.pub_date
    
