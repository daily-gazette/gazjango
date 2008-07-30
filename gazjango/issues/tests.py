import unittest
from articles.models      import Article, Category, Format
from announcements.models import Announcement
from issues.models        import Issue, IssueArticle, IssueAnnouncement
from datetime import date, timedelta

class IssueTestCase(unittest.TestCase):
    
    def setUp(self):
        self.news     = Category.objects.create(name="News", slug="news")
        self.features = Category.objects.create(name="Features", slug="features")
        self.html = Format.objects.create(name="Plain HTML", function="html")
        
        b = dict(headline="Boring", text="Text", slug="boring", 
                 category=self.news, format=self.html)
        self.boring_article = Article.objects.create(**b)
        
        e = dict(headline="Excitement", text="Text", slug="exciting", 
                 category=self.features, format=self.html)
        self.exciting_article = Article.objects.create(**e)
        
        self.issue_today = Issue.objects.create()
        yesterday = date.today() - timedelta(days=1)
        self.issue_yesterday = Issue.objects.create(date=yesterday)
    
    def tearDown(self):
        ms = (Article, Announcement, Category, Format, Issue)
        for m in ms + (IssueArticle, IssueAnnouncement):
            m.objects.all().delete()
    
    def testOrdering(self):
        self.issue_today.add_article(self.boring_article)
        self.assert_(self.issue_today.articles.count() == 1)
        self.assert_(self.issue_yesterday.articles.count() == 0)
        
        self.issue_yesterday.add_article(self.boring_article)
        self.assert_(self.issue_today.articles.count() == 1)
        self.assert_(self.issue_yesterday.articles.count() == 1)
        
        fail = lambda: self.issue_today.add_article(self.boring_article)
        self.assertRaises(Exception, fail)
        
        self.assertEquals(self.issue_today.get_issuearticle_order(),
                [self.boring_article.issuearticle_set.get(issue=self.issue_today).pk])
        
        self.issue_today.add_article(self.exciting_article)
        boring_ia   = self.boring_article.issuearticle_set.get(  issue=self.issue_today)
        exciting_ia = self.exciting_article.issuearticle_set.get(issue=self.issue_today)
        
        self.assertEquals(self.issue_today.get_issuearticle_order(),
                          [boring_ia.pk, exciting_ia.pk])
        
        self.issue_today.set_issuearticle_order([exciting_ia.pk, boring_ia.pk])
        self.assertEquals([a.pk for a in self.issue_today.articles_in_order().all()], 
                         [self.exciting_article.pk, self.boring_article.pk])
    
