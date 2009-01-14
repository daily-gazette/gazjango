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
    
    def get_concepts(self, user, base=None):
        """
        Returns story concepts, ordered by their status and then by their due date.
        """    
        base = base or self
        
        users = base.filter(users=user).exclude(due__lt=date.today).order_by('due')
        others = base.exclude(users=user).order_by('due')
        others = others.exclude(users=None).order_by('due')
        unclaimed = base.filter(users=None).order_by('due')
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
    
