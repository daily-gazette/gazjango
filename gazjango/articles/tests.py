import unittest
from django.core.exceptions     import ObjectDoesNotExist, MultipleObjectsReturned
from django.contrib.auth.models import User
from articles.models import Article, ArticleRevision, Section, Format
from accounts.models import UserProfile, UserKind
from media.models    import MediaBucket, MediaFile, ImageFile
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
                 '<img src="o-rly" />.\n\n'
                 'In far more serious news, Canada declared war on Mexico. '
                 '<img src="from-the-newspapers/war-declared" /> '
                 "Here's another image, just for kicks: "
                 '<img src="http://wow.com/lawl" />',
            bucket=self.bucket,
            slug='lolcats',
            section=self.news,
            format=self.html
        )
        
        self.textile_images_article = Article.objects.create(
            headline="Brief Test For Textile",
            text="!war-declared!",
            bucket=self.bucket2,
            section=self.news,
            format=self.textile
        )
    
    def tearDown(self):
        used = (User, UserProfile, UserKind, Section, Article, ArticleRevision, Format)
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
        self.assertEquals(self.formatted_article.formatted_text(),
                          "<p><em>Emphasis</em></p>")
        self.formatted_article.format = self.html
        self.assertEquals(self.formatted_article.formatted_text(),
                          self.formatted_article.text)
    
    
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
        
        # by bucket/slug, non-existant file
        self.assertRaises(ObjectDoesNotExist,
                          lambda: resolve('fake-bucket/fakery', complain=True))
        self.assertEquals(resolve('fake-bucket/fakery', complain=False), "")
        
        # by slug with a duplicate in media
        bucket = MediaBucket.objects.create(slug='trickster')
        self.images_article.media.create(slug="kitteh", bucket=bucket, data="")
        
        self.assertRaises(MultipleObjectsReturned, 
                          lambda: resolve("kitteh", complain=True))
        self.assertEquals(resolve('kitteh', complain=False),
                          "[ambiguous reference to 'kitteh']")
    
    
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
        
        top1 = art(slug='squirrel-attack', position='t', possible_position='t')
        assert_pks([ [top1.pk], [], [] ])
        
        mid1 = art(slug='this-weekend', position='m', possible_position='m')
        assert_pks([ [top1.pk], [mid1.pk], [] ])
        
        top2 = art(slug='squirrel-hunt', position='t', possible_position='t')
        assert_pks_gives( [ [top1.pk], [top2.pk, mid1.pk], [] ],
                          [ [top2.pk], [top1.pk, mid1.pk], [] ] )
        
        low_mid1 = art(slug='concert-last-week', position='n', possible_position='m')
        assert_pks_gives( [ [top1.pk], [top2.pk, mid1.pk], [low_mid1.pk] ],
                          [ [top2.pk], [top1.pk, mid1.pk], [low_mid1.pk] ] )
        
        top2.delete()
        assert_pks([ [top1.pk], [mid1.pk, low_mid1.pk], [] ])
        
        low_top1 = art(slug='deer-all-dead', position='n', possible_position='t',
                       pub_date=date.today() - timedelta(days=1))
        assert_pks([ [top1.pk], [mid1.pk, low_mid1.pk], [low_top1.pk] ])
        
        top1.delete()
        assert_pks([ [low_top1.pk], [mid1.pk, low_mid1.pk], [] ])
        
        mid2 = art(slug='why-are-there-so-many-penn-stations', 
                   position='m', possible_position='m')
        assert_pks_gives( [ [low_top1.pk], [mid1.pk, mid2.pk], [low_mid1.pk] ],
                          [ [low_top1.pk], [mid2.pk, mid1.pk], [low_mid1.pk] ] )
        
        mid3 = art(slug='something-happened', position='m', possible_position='m')
        assert_pks_gives( [ [low_top1.pk], [mid1.pk, mid2.pk], [mid3.pk, low_mid1.pk] ],
                          [ [low_top1.pk], [mid1.pk, mid3.pk], [mid2.pk, low_mid1.pk] ],
                          [ [low_top1.pk], [mid2.pk, mid1.pk], [mid3.pk, low_mid1.pk] ],
                          [ [low_top1.pk], [mid2.pk, mid3.pk], [mid1.pk, low_mid1.pk] ],
                          [ [low_top1.pk], [mid3.pk, mid1.pk], [mid2.pk, low_mid1.pk] ],
                          [ [low_top1.pk], [mid3.pk, mid2.pk], [mid1.pk, low_mid1.pk] ] )
    
