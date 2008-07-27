import unittest
from django.contrib.auth.models import User
from accounts.models            import UserProfile, Position, PositionHeld, UserKind
from articles.models            import Article
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
        for m in (User, UserProfile, Position, PositionHeld, UserKind):
            m.objects.all().delete()
    
    def test_positions_empty(self):
        self.assertEquals(len(self.bob.get_profile().current_positions()), 0)
        for pos in Position.objects.all():
            self.assertEquals(pos.holdings.count(), 0)
    
    def test_current_positions(self):
        p = self.bob.get_profile()
        
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow  = today + timedelta(days=1)
        
        p.add_position(self.reader)
        self.assertEquals(p.positions_held.count(), 1)
        self.assertEquals(p.current_positions()[0], self.reader)
        self.assertEquals(p.position(), self.reader)
        
        p.add_position(self.reporter, today, tomorrow)
        self.assertEquals(p.positions_held.count(), 2)
        self.assertEquals(set(p.current_positions()), 
                          set([self.reader, self.reporter]))
        self.assertEquals(p.position(), self.reporter)
        self.assertEquals(p.position_at(today + timedelta(days=2)), self.reader)
        
        p.add_position(self.editor, date.today() + timedelta(days=4))
        self.assertEquals(p.positions_held.count(), 3)
        self.assertEquals(set(p.current_positions()),
                          set([self.reader, self.reporter]))
        self.assertEquals(p.position(), self.reporter)
        self.assertEquals(p.position_at(today + timedelta(days=4)), self.editor)
        
        reader = p.positions_held.get(position=self.reader)
        reader.date_end = date.today() - timedelta(days=1)
        reader.save()
        self.assertEquals(p.positions_held.count(), 3)
        self.assertEquals(set(p.current_positions()),
                          set([self.reporter]))
        self.assertEquals(p.position(), self.reporter)
        
        editor = p.positions_held.get(position=self.editor)
        editor.date_start = date.today()
        editor.save()
        self.assertEquals(p.positions_held.count(), 3)
        self.assertEquals(set(p.current_positions()),
                          set([self.reporter, self.editor]))
        self.assertEquals(p.position(), self.editor)
    
