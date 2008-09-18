import unittest
from django.contrib.auth.models import User, AnonymousUser
from gazjango.articles.models   import Article, Section, Format
from gazjango.accounts.models   import UserProfile, UserKind
from gazjango.polls.models      import Poll, Option
from datetime                   import datetime, timedelta

class PollTestCase(unittest.TestCase):
    
    def setUp(self):
        oh_ten = UserKind.objects.create(kind='s', year=2010)
        self.bob = User.objects.create_user("bob", "bob@example.com")
        self.bob.userprofile_set.add(UserProfile(kind=oh_ten))
        
        self.john = User.objects.create_user("john", "john@example.com")
        self.john.userprofile_set.add(UserProfile(kind=oh_ten))
        
        self.anon = AnonymousUser()
        self.anon_ip = '102.178.2.4'
        
        self.news = Section.objects.create(name="News")

        self.html = Format.objects.create(name     = "html",
                                          function = "html")

        self.boring_article = Article.objects.create(headline = "...Boring",
                                                     text     = "Boring Text",
                                                     section  = self.news,
                                                     format   = self.html)
        p = self.exciting_poll = Poll.objects.create(
            name="Exciting Poll",
            question = "Does this poll excite you?",
            article  = self.boring_article,
            time_start = datetime.now(),
            time_stop  = datetime.now() + timedelta(days=1))
        self.options = {
            'yes': Option.objects.create(name="yes", poll=p),
            'no':  Option.objects.create(name="no",  poll=p)
        }
    
    def tearDown(self):
        for m in (User, UserProfile, UserKind, Section, Article, Format, Poll, Option):
            m.objects.all().delete()
        del self.anon
        
    
    def test_poll_creation(self):
        p = self.exciting_poll
        self.assertEquals(set([0]), set([o.votes for o in p.options.all()]))
        self.assert_(p.voting())
        
        for val in (True, False):
            p.allow_anon = val
            self.assert_(p.can_vote(self.john))
            self.assert_(p.can_vote(self.bob))
            self.assertEquals(p.can_vote(self.anon), val)
    
    def test_poll_voting(self):
        p = self.exciting_poll
        os = self.options
        
        self.assert_(p.vote(user=self.bob, option=os['yes']))
        self.assertEquals(os['yes'].votes(), 1)
        self.assertEquals(os['no'].votes(),  0)
        self.assertEquals([o.pk for o in p.results()], 
                          [os['yes'].pk, os['no'].pk])
        self.assert_(not p.can_vote(user=self.bob))
        
        self.assert_(p.vote(user=self.john, option=os['no']))
        self.assertEquals(os['yes'].votes(), 1)
        self.assertEquals(os['no'].votes(),  1)
        self.assert_(not p.can_vote(user=self.john))
        
        p.allow_anon = True
        self.assert_(p.vote(user=self.anon, ip=self.anon_ip, option=os['yes']))
        self.assertEquals(os['yes'].votes(), 2)
        self.assertEquals(os['no'].votes(),  1)
        
        
