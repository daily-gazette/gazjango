import unittest
from django.core.exceptions     import ObjectDoesNotExist, MultipleObjectsReturned
from django.contrib.auth.models import User
from gazjango.articles.models import Article, ArticleRevision, Section, Format
from gazjango.accounts.models import UserProfile, UserKind
from gazjango.media.models    import MediaBucket, MediaFile, ImageFile
from datetime import date, timedelta

class ArticleTestCase(unittest.TestCase):
    
    def setUp(self):
        oh_ten = UserKind.objects.create(kind='s', year=2010)
        self.bob = User.objects.create_user("bob", 'bob@example.com')
        self.bob.userprofile_set.add(UserProfile(kind=oh_ten))
        self.bob_profile = self.bob.get_profile()
        
        self.news = Section.objects.create(name="News")
        
        self.textile = Format.objects.create(name     = "textile",
                                             function = "textile")
        self.html = Format.objects.create(name     = "html",
                                          function = "html")

        self.boring_article = Article.objects.create(headline = "...Boring",
                                                     text     = "Boring Text",
                                                     slug     = 'boring',
                                                     section = self.news,
                                                     format   = self.html)
        
        self.formatted_article = Article.objects.create(headline = "Formatted!",
                                                        text     = "_Emphasis_",
                                                        slug     = "formatted",
                                                        section = self.news,
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
                 '<img src="from-the-internets/o-rly" />.\n\n'
                 'In far more serious news, Canada declared war on Mexico. '
                 '<img src="from-the-newspapers/war-declared" /> '
                 "Here's another image, just for kicks: "
                 '<img src="http://wow.com/lawl" />',
            slug='lolcats',
            section=self.news,
            format=self.html
        )
        
        self.textile_images_article = Article.objects.create(
            headline="Brief Test For Textile",
            text="!from-the-newspapers/war-declared!",
            section=self.news,
            format=self.textile
        )
    
    def tearDown(self):
        used = (User, UserProfile, UserKind, Section, Article, ArticleRevision)
        for m in used + (Format, MediaBucket, MediaFile, ImageFile):
            m.objects.all().delete()
    
    def test_articles_empty(self):
        self.assertEquals(len(self.bob_profile.articles.all()), 0)
        self.assertEquals(len(self.boring_article.authors.all()), 0)
    
    def test_article_creation(self):
        self.boring_article.add_author(self.bob_profile)
        self.assert_(self.boring_article in self.bob_profile.articles.all())
        self.assert_(self.bob_profile in self.boring_article.authors.all())
        self.assertTrue(self.boring_article.allow_edit(self.bob))
    
    def test_article_revision(self):
        a = self.boring_article
        a.add_author(self.bob_profile) # needed for reviser
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
        self.assertEquals(self.formatted_article.formatted_text(),
                          "<p><em>Emphasis</em></p>")
        self.formatted_article.format = self.html
        self.assertEquals(self.formatted_article.formatted_text(),
                          self.formatted_article.text)
    
    
    def test_link_resolution(self):
        resolve = self.images_article.resolve_media_link
        
        is_in_media = lambda obj: \
            self.images_article.media.filter(pk=obj.pk).count() == 1
        
        owl_url = self.owl.get_absolute_url()
        lolcat_url = self.lolcat.get_absolute_url()
        war_url = self.war.get_absolute_url()
                
        # not in media
        self.assert_(not is_in_media(self.lolcat))
        self.assertEquals(resolve('from-the-internets/kitteh'), lolcat_url)
        self.assert_(is_in_media(self.lolcat))
        
        # different bucket, not in media
        self.assert_(not is_in_media(self.war))
        self.assertEquals(resolve('from-the-newspapers/war-declared'), war_url)
        self.assert_(is_in_media(self.war))
        
        # first bucket, in media
        self.assertEquals(resolve('from-the-internets/o-rly'), owl_url)
        
        # other bucket, in media
        self.assertEquals(resolve('from-the-newspapers/war-declared'), war_url)
        
        # non-existant file
        self.assertRaises(ObjectDoesNotExist,
                          lambda: resolve('fake-bucket/fakery', complain=True))
        self.assertEquals(resolve('fake-bucket/fakery', complain=False), "")    
    
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
    
    
    def test_get_stories(self):
        Article.objects.all().delete()
        
        get_stories = Article.published.get_stories
        def get_pks(**args):
            res = get_stories(**args)
            return [ [story.pk for story in lst] for lst in res ]
        
        def assert_pks(pks, **args):
            self.assertEqual(get_pks(**args), pks)
        
        def assert_pks_gives(*possibilities, **args):
            to_see = [poss for poss in possibilities]
            for i in range(len(possibilities) * 8):
                pks = get_pks(**args)
                self.assert_(pks in possibilities, "%s not in %s" % (pks, possibilities))
                try:
                    to_see.remove(pks)
                except ValueError:
                    pass
                
                if len(to_see) == 0:
                    return
            self.assertEqual(len(to_see), 0)
        
        def art(**args):
            args.setdefault('format', self.textile)
            args.setdefault('status', 'p')
            args.setdefault('section', self.news)
            return Article.objects.create(**args)
        
        top1 = art(slug='squirrel-attack', position='1', possible_position='1')
        assert_pks([ [top1.pk], [], [] ])
        
        mid1 = art(slug='this-weekend', position='2', possible_position='2')
        assert_pks([ [top1.pk], [mid1.pk], [] ])
        
        top2 = art(slug='squirrel-hunt', position='1', possible_position='1')
        assert_pks_gives( [ [top1.pk], [top2.pk, mid1.pk], [] ],
                          [ [top2.pk], [top1.pk, mid1.pk], [] ] )
        
        low_mid1 = art(slug='concert-last-week', position='3', possible_position='2')
        assert_pks_gives( [ [top1.pk], [top2.pk, mid1.pk], [low_mid1.pk] ],
                          [ [top2.pk], [top1.pk, mid1.pk], [low_mid1.pk] ] )
        
        top2.delete()
        assert_pks([ [top1.pk], [mid1.pk, low_mid1.pk], [] ])
        
        low_top1 = art(slug='deer-all-dead', position='3', possible_position='2',
                       pub_date=date.today() - timedelta(days=1))
        assert_pks([ [top1.pk], [mid1.pk, low_mid1.pk], [low_top1.pk] ])
        
        top1.delete()
        assert_pks([ [low_top1.pk], [mid1.pk, low_mid1.pk], [] ])
        
        mid2 = art(slug='why-are-there-so-many-penn-stations', 
                   position='2', possible_position='2')
        assert_pks_gives( [ [low_top1.pk], [mid1.pk, mid2.pk], [low_mid1.pk] ],
                          [ [low_top1.pk], [mid2.pk, mid1.pk], [low_mid1.pk] ] )
        
        mid3 = art(slug='something-happened', position='2', possible_position='2')
        assert_pks_gives( [ [low_top1.pk], [mid1.pk, mid2.pk], [mid3.pk, low_mid1.pk] ],
                          [ [low_top1.pk], [mid1.pk, mid3.pk], [mid2.pk, low_mid1.pk] ],
                          [ [low_top1.pk], [mid2.pk, mid1.pk], [mid3.pk, low_mid1.pk] ],
                          [ [low_top1.pk], [mid2.pk, mid3.pk], [mid1.pk, low_mid1.pk] ],
                          [ [low_top1.pk], [mid3.pk, mid1.pk], [mid2.pk, low_mid1.pk] ],
                          [ [low_top1.pk], [mid3.pk, mid2.pk], [mid1.pk, low_mid1.pk] ] )
    
