import unittest
from django.contrib.auth.models import User
from accounts.models            import UserProfile, Position, PositionHeld
from articles.models            import Article

class UserTestCase(unittest.TestCase):
    def setUp(self):
        self.bob = User.objects.create_user('bob', 'bob@example.com')
        self.bob.userprofile_set.add(UserProfile())
        
        self.reader   = Position.objects.create(name="Reader")
        self.reporter = Position.objects.create(name="Staff Reporter")
        self.editor   = Position.objects.create(name="Arts Editor")
    
    def tearDown(self):
        for x in (self.bob, self.reader, self.reporter, self.editor):
            x.delete()
    
    def test_positions_empty(self):
        self.assertEquals(len(self.bob.get_profile().current_positions()), 0)
        for pos in Position.objects.all():
            self.assertEquals(pos.holdings.count(), 0)
    
    def test_current_positions(self):
        p = self.bob.get_profile()
        
        p.add_position(self.reader)
        self.assertEquals(p.positions.count(), 1)
        self.assertEquals(p.current_positions()[0].position, self.reader)
        
        p.add_position(self.reporter)
        self.assertEquals(p.positions.count(), 2)
        self.assertEquals(set([ph.position for ph in p.current_positions()]), 
                          set([self.reader, self.reporter]))
    
