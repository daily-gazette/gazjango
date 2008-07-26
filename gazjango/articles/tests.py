import unittest
from django.core.exceptions     import ObjectDoesNotExist, MultipleObjectsReturned
from django.contrib.auth.models import User
from articles.models import Article, ArticleRevision, Category, Format
from accounts.models import UserProfile
from media.models    import MediaBucket, MediaFile, ImageFile

class ArticleTestCase(unittest.TestCase):
    
    def setUp(self):
        self.bob = User.objects.create_user("bob", 'bob@example.com')
        self.bob.userprofile_set.add(UserProfile())
        self.bob_profile = self.bob.get_profile()
        
        self.news = Category.objects.create(name="News")
        
        self.textile = Format.objects.create(name     = "textile",
                                             function = "textile")
        self.html = Format.objects.create(name     = "html",
                                          function = "html")

        self.boring_article = Article.objects.create(headline = "...Boring",
                                                     text     = "Boring Text",
                                                     slug     = 'boring',
                                                     category = self.news,
                                                     format   = self.html)
        self.formatted_article = Article.objects.create(headline = "Formatted!",
                                                        text     = "_Emphasis_",
                                                        slug     = "formatted",
                                                        category = self.news,
                                                        format   = self.textile)
        
        self.bucket = MediaBucket.objects.create(slug='from-the-internets')
        self.lolcat = ImageFile.objects.create(slug='kitteh',
                                               bucket=self.bucket,
                                               data='uploads/lolcat.jpg')
        self.owl    = ImageFile.objects.create(slug="o-rly",
                                               bucket=self.bucket,
                                               data='uploads/orly.png')
        self.bucket2 = MediaBucket.objects.create(slug='from-the-newspapers')
        self.war = ImageFile.objects.create(slug='war-declared',
                                            bucket=self.bucket2,
                                            data='uploads/big-war-started.png')
        self.images_article = Article.objects.create(
            headline="Lolcats Are Kinda Sweet, But Also Kinda Lame",
            text="Here's an example: "
                 '<img width="10" src="from-the-internets/kitteh"/>.\n\n'
                 'Some see them as similar to the so-called "o rly?" owls: '
                 '<img src="o-rly" />.\n\n'
                 'In far more serious news, Canada declared war on Mexico. '
                 '<img src="from-the-newspapers/war-declared" /> '
                 "Here's another image, just for kicks: "
                 '<img src="http://wow.com/lawl" />',
            bucket=self.bucket,
            slug='lolcats',
            category=self.news,
            format=self.html
        )
        
        self.textile_images_article = Article.objects.create(
            headline="Brief Test For Textile",
            text="!war-declared!",
            bucket=self.bucket2,
            category=self.news,
            format=self.textile
        )
    
    def tearDown(self):
        used = (User, UserProfile, Category, Article, ArticleRevision, Format)
        for m in used + (MediaBucket, MediaFile, ImageFile):
            m.objects.all().delete()
    
    def test_articles_empty(self):
        self.assertEquals(len(self.bob_profile.articles.all()), 0)
        self.assertEquals(len(self.boring_article.authors.all()), 0)
    
    def test_article_creation(self):
        self.bob.get_profile().articles.add(self.boring_article)
        self.assert_(self.boring_article in self.bob_profile.articles.all())
        self.assert_(self.bob_profile in self.boring_article.authors.all())
        self.assertTrue(self.boring_article.allow_edit(self.bob))
    
    def test_article_revision(self):
        a = self.boring_article
        strs = (a.text,
                "Boring Text (!)", 
                "Boring Text (with some boring revisions)",
                "Lame-Text-Extreme (with moderately less-boring revisions made)")
        
        for i in range(1, len(strs)):
            a.revise_text(strs[i])
            self.assertEquals(a.text, strs[i])
            rs = a.revisions.reverse()
            for j in range(i):
                self.assertEquals(a.text_at_revision(rs[j]), strs[j])
    
    def test_article_formatting(self):
        self.formatted_article.format = self.textile
        self.assertEquals(self.formatted_article.formatted_text(), "<p><em>Emphasis</em></p>")
        self.formatted_article.format = self.html
        self.assertEquals(self.formatted_article.formatted_text(), self.formatted_article.text)
    
    
    def test_link_resolution(self):
        resolve = self.images_article.resolve_image_link
        
        is_in_media = lambda obj: \
            self.images_article.media.filter(pk=obj.pk).count() == 1
        
        owl_url = self.owl.get_absolute_url()
        lolcat_url = self.lolcat.get_absolute_url()
        war_url = self.war.get_absolute_url()
        
        # by slug only, default bucket, not in media
        self.assert_(not is_in_media(self.owl))
        self.assertEquals(resolve('o-rly'), owl_url)
        self.assert_(is_in_media(self.owl))
        
        # by bucket/slug, default bucket, not in media
        self.assert_(not is_in_media(self.lolcat))
        self.assertEquals(resolve('from-the-internets/kitteh'), lolcat_url)
        self.assert_(is_in_media(self.lolcat))
        
        # by slug only, different bucket, not in media
        self.assert_(not is_in_media(self.war))
        self.assertRaises(ObjectDoesNotExist, 
                          lambda: resolve('war-declared', complain=True))
        self.assertEquals(resolve('war-declared', complain=False), '')
        
        # by bucket/slug, different bucket, not in media
        self.assert_(not is_in_media(self.war))
        self.assertEquals(resolve('from-the-newspapers/war-declared'), war_url)
        self.assert_(is_in_media(self.war))
        
        # by slug only, default bucket, in media
        self.assertEquals(resolve('kitteh'), lolcat_url)
        
        # by bucket/slug, default bucket, in media
        self.assertEquals(resolve('from-the-internets/o-rly'), owl_url)
        
        # by slug only, other bucket, in media
        self.assertEquals(resolve('war-declared'), war_url)
        
        # by bucket/slug, other bucket, in media
        self.assertEquals(resolve('from-the-newspapers/war-declared'), war_url)
    
    def test_resolved_text(self):
        resolved = self.images_article.resolved_text()
        expected = 'Here\'s an example: <img width="10" src="%s" />.\n\n' \
                   'Some see them as similar to the so-called "o rly?" owls: ' \
                   '<img src="%s" />.\n\n' \
                   'In far more serious news, Canada declared war on Mexico. ' \
                   '<img src="%s" /> Here\'s another image, just for kicks: ' \
                   '<img src="http://wow.com/lawl" />'
        formats = [x.get_absolute_url() for x in (self.lolcat, self.owl, self.war)]
        self.assertEqual(resolved, expected % tuple(formats))
        
        resolved = self.textile_images_article.resolved_text()
        expected = '<p><img src="%s" alt="" /></p>'
        self.assertEqual(resolved, expected % self.war.get_absolute_url())
    
