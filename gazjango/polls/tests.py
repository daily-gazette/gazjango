import unittest
from django.contrib.auth.models import User, AnonymousUser
from articles.models            import Article, Category
from accounts.models            import UserProfile
from polls.models               import Poll, Option
from datetime                   import datetime, timedelta

class PollTestCase(unittest.TestCase):
    
    def setUp(self):
        self.bob = User.objects.create_user("bob", "bob@example.com")
        self.bob.userprofile_set.add(UserProfile())
        
        self.john = User.objects.create_user("john", "john@example.com")
        self.john.userprofile_set.add(UserProfile())
        
        self.anon = AnonymousUser()
        
        self.news = Category.objects.create(name="News")
        self.boring_article = Article.objects.create(headline = "...Boring",
                                                     text     = "Boring Text",
                                                     category = self.news)
        p = self.exciting_poll = Poll.objects.create(
            name="Exciting Poll",
            question = "Does this poll excite you?",
            article  = self.boring_article,
            time_start = datetime.now(),
            time_stop  = datetime.now() + timedelta(days=1))
        self.options = {
            'yes': Option.objects.create(name="yes", description="Yes", poll=p),
            'no':  Option.objects.create(name="no",  description="No",  poll=p)
        }
    
    def tearDown(self):
        for m in (User, UserProfile, Category, Article, Poll, Option):
            m.objects.all().delete()
        del self.anon
        
    
    def test_poll_creation(self):
        p = self.exciting_poll
        self.assertEquals(set([0]), set([o.votes for o in p.option_set.all()]))
        self.assert_(p.voting())
        
        for val in (True, False):
            p.allow_anon = val
            self.assert_(p.can_vote(self.john))
            self.assert_(p.can_vote(self.bob))
            self.assertEquals(p.can_vote(self.anon), val)
    
    def test_poll_voting(self):
        p = self.exciting_poll
        os = self.options
        
        self.assert_(p.vote(self.bob, os['yes']))
        self.assertEquals(os['yes'].votes, 1)
        self.assertEquals(os['no'].votes,  0)
        self.assertEquals([o.pk for o in p.results()], 
                          [os['yes'].pk, os['no'].pk])
        self.assert_(not p.can_vote(self.bob))
        
        self.assert_(p.vote(self.john, os['no']))
        self.assertEquals(os['yes'].votes, 1)
        self.assertEquals(os['no'].votes,  1)
        self.assert_(not p.can_vote(self.john))
        
        p.allow_anon = True
        self.assert_(p.vote(self.anon, os['yes']))
        self.assertEquals(os['yes'].votes, 2)
        self.assertEquals(os['no'].votes,  1)
        self.assertEquals([o.pk for o in p.results()], 
                          [os['yes'].pk, os['no'].pk])
        
        