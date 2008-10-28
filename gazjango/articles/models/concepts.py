from django.db import models
from gazjango.accounts.models         import UserProfile
from gazjango.articles.models.stories import Article
from datetime import date
from gazjango.misc.templatetags.extras import join_authors


class UnpublishedConceptsManager(models.Manager):
    "A manager for StoryConcepts that only deals with concepts not yet published."
    def get_query_set(self):
        orig = super(UnpublishedConceptsManager, self).get_query_set()
        return orig.exclude(status='p')
        
    def get_concepts(self, user, base=None):
        """
        Returns story concepts, ordered by their status and then by their due date.
        """
        
        base = base or self
        
        users = list(base.filter(users=user).order_by('due'))
        others = list(base.exclude(users=user).exclude(users=None).order_by('due'))
        unclaimed = list(base.filter(users=None).order_by('due'))
        
        return [users, others, unclaimed]
    

class StoryConcept(models.Model):
    """
    An idea for a story. Assigned to user(s), where it then shows
    up on their (and others') dashboards to let people know they're
    working on it. Has a status, articles based on it, a due date,
    and comments.
    """
    
    # hardcoded because we have code (namely UnpublishedConceptsManager)
    # that refers to whether the story is complete or not. lame, i know 
    STATUSES = (
        ('a', 'assigned'),
        ('i', 'researching'),
        ('w', 'writing - research mostly done'),
        ('e', 'revising'),
        ('s', 'submitted to editors'),
        ('r', 'significant revisions after editing'),
        ('p', 'published')
    )
    
    name  = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    due   = models.DateField(default=date.today)
    status = models.CharField(max_length=1, choices=STATUSES, default='a')
    
    users   = models.ManyToManyField(UserProfile, blank=True, related_name="assignments")
    
    
    """
    // editor   = models.ManyToManyField(UserProfile, related_name="overseer")
    I'd like to be able to call an editor's email address too, from contact information.
    
    Also ... is there any way to get the story's number, so that the whole page can be linked into the admin?
    """

    article = models.ForeignKey(Article, null=True, blank=True, unique=True,
                                related_name="concepts")
    
    objects = models.Manager()
    unpublished = UnpublishedConceptsManager()
    
    class Meta:
        app_label = 'articles'
    
    def notes_excerpt(self, length=60):
        "Returns the first `length` chars of notes."
        if len(self.notes) <= length:
            return self.notes
        else:
            return self.notes[:length-3] + '...'

	def get_name(self):
		"""Returns the name of the story concept"""
		return self.name
	
	def get_notes(self):
		"""Returns the story notes"""
		return self.notes
		
	def date_due(self):
		return self.due
		
	def status(self):
		return self.status
		
	def users_in_order(self):
		return self.users
	
	def user_names(self):
		return join_authors(self.users_in_order(), 'ptx')
    
    def __unicode__(self):
        return self.name
    
