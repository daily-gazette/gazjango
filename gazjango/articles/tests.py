import unittest
from django.contrib.auth.models import User, Permission
from articles.models import Article
from accounts.models import UserProfile

class ArticleTestCase(unittest.TestCase):

    def setUp(self):
        self.bob = User.objects.create(username="bob")
        self.bob.userprofile_set.add(UserProfile())
        self.boring_article = Article.objects.create(headline="Something Boring",
                                                     text="Boring Text")

    def tearDown(self):
        self.bob.delete()
        self.boring_article.delete()

    def test_articles_empty(self):
        self.assertEquals(len(self.bob.get_profile().articles.all()), 0)

    def test_article_creation(self):
        self.bob.get_profile().articles.add(self.boring_article)
        self.assert_(self.boring_article in self.bob.get_profile().articles.all())
        self.assert_(self.bob.get_profile() in self.boring_article.authors.all())
        self.assertTrue(self.boring_article.allow_edit(self.bob))
