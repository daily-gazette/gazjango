import unittest
from django.contrib.auth.models import User, Permission
from articles.models            import Article, Category
from accounts.models            import UserProfile

class ArticleTestCase(unittest.TestCase):
    
    def setUp(self):
        self.bob = User.objects.create(username="bob")
        self.bob.userprofile_set.add(UserProfile())
        self.bob_profile = self.bob.get_profile()
        
        self.news = Category.objects.create(name="News")
        self.boring_article = Article.objects.create(headline = "...Boring",
                                                     text     = "Boring Text",
                                                     category = self.news)
    
    def tearDown(self):
        self.bob.delete()
        self.boring_article.delete()
    
    def test_articles_empty(self):
        self.assertEquals(len(self.bob_profile.articles.all()), 0)
        self.assertEquals(len(self.boring_article.authors.all()), 0)
    
    def test_article_creation(self):
        self.bob.get_profile().articles.add(self.boring_article)
        self.assert_(self.boring_article in self.bob_profile.articles.all())
        self.assert_(self.bob_profile in self.boring_article.authors.all())
        self.assertTrue(self.boring_article.allow_edit(self.bob))
