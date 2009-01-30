from django.db                         import models
from gazjango.accounts.models          import UserProfile
from datetime                          import date
from gazjango.misc.templatetags.extras import join_authors
from gazjango.announcements.models     import Announcement


class UnpublishedConceptsManager(models.Manager):
    "A manager for StoryConcepts that only deals with concepts not yet published."
    def get_query_set(self):
        orig = super(UnpublishedConceptsManager, self).get_query_set()
        return orig.exclude(status='p')
		
	def get_upcoming_concepts(self):
		"""
		Returns the story concepts from the next 3 days.
		"""
		
		base = None or self
		
		claimed = base.exclude(users=None).order_by('due')
		unclaimed = base.filters(users=None).order_by('due')
		
		return [claimed,unclaimed]		
    
    def get_concepts(self, user, base=None):
        """
        Returns story concepts, ordered by their status and then by their due date.
        """    
        base = base or self
        
        users = base.filter(users=user).order_by('due')
        others = base.exclude(users=user).exclude(users=None).order_by('due')
        unclaimed = base.filter(users=None).order_by('due')
        return [users, others, unclaimed]
    

class StoryConcept(models.Model):
    """
    An idea for a story. Assigned to user(s), where it then shows
    up on their (and others') dashboards to let people know they're
    working on it. Has a status, articles based on it, a due date,
    and comments.
    """
    
    STATUSES = (
        ('u', 'unassigned'),
        ('a', 'assigned / working on it'),
        ('p', 'published'),
    )
    
    name  = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    due   = models.DateField(blank=True, null=True, default=None)
    status = models.CharField(max_length=1, choices=STATUSES, default='u')
    
    users   = models.ManyToManyField(UserProfile, blank=True, related_name="assignments")
    # editors = models.ManyToManyFiled(UserProfile, related_name="concepts_overseen")
    
    objects = models.Manager()
    unpublished = UnpublishedConceptsManager()
    
    def notes_excerpt(self, length=60):
        "Returns the first `length` chars of notes."
        if len(self.notes) <= length:
            return self.notes
        else:
            return self.notes[:length-3] + '...'
    
    def user_names(self):
        return join_authors(self.users, 'ptx')
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        app_label = 'articles'
    
