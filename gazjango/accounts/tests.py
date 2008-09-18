import unittest
from django.contrib.auth.models import User
from gazjango.accounts.models   import UserProfile, Position, Holding, UserKind
from gazjango.articles.models   import Article
from datetime                   import date, datetime, timedelta

class UserTestCase(unittest.TestCase):
    def setUp(self):
        self.student = UserKind.objects.create(kind='s', year=2010)
        
        self.bob = User.objects.create_user('bob', 'bob@example.com')
        self.bob_p = self.bob.userprofile_set.create(kind=self.student)
        
        self.reader   = Position.objects.create(name="Reader",         rank=0)
        self.reporter = Position.objects.create(name="Staff Reporter", rank=5)
        self.editor   = Position.objects.create(name="Arts Editor",    rank=9)
    
    def tearDown(self):
        for m in (User, UserProfile, Position, Holding, UserKind):
            m.objects.all().delete()
    
    def test_positions_empty(self):
        self.assertEquals(len(self.bob.get_profile().current_positions()), 0)
        for pos in Position.objects.all():
            self.assertEquals(pos.holdings.count(), 0)
    
    def test_positions(self):
        bob = self.bob.get_profile()
        
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow  = today + timedelta(days=1)
        
        bob.add_position(self.reader)
        self.assertEquals(bob.current_positions().count(), 1)
        self.assertEquals(bob.current_positions()[0], self.reader)
        self.assertEquals(bob.position(), self.reader)
        
        bob.add_position(self.reporter, today, tomorrow)
        self.assertEquals(bob.current_positions().count(), 2)
        self.assertEquals(set(bob.current_positions()), 
                          set([self.reader, self.reporter]))
        self.assertEquals(bob.position(), self.reporter)
        self.assertEquals(bob.position_at(today + timedelta(days=2)), self.reader)
        
        bob.add_position(self.editor, date.today() + timedelta(days=4))
        self.assertEquals(bob.current_positions().count(), 2)
        self.assertEquals(set(bob.current_positions()),
                          set([self.reader, self.reporter]))
        self.assertEquals(bob.position(), self.reporter)
        self.assertEquals(bob.position_at(today + timedelta(days=4)), self.editor)
        
        reader = bob.holding_set.get(position=self.reader)
        reader.date_end = date.today() - timedelta(days=1)
        reader.save()
        self.assertEquals(bob.current_positions().count(), 1)
        self.assertEquals(set(bob.current_positions()),
                          set([self.reporter]))
        self.assertEquals(bob.position(), self.reporter)
        
        editor = bob.holding_set.get(position=self.editor)
        editor.date_start = date.today()
        editor.save()
        self.assertEquals(bob.current_positions().count(), 2)
        self.assertEquals(set(bob.current_positions()),
                          set([self.reporter, self.editor]))
        self.assertEquals(bob.position(), self.editor)
    
