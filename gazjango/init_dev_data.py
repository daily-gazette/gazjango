#!/usr/bin/env python

import settings
from django.core.management import setup_environ
setup_environ(settings)

### imports

from datetime import date, datetime, timedelta, time
import random

from django.contrib.auth.models         import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models        import Site
from django.contrib.flatpages.models    import FlatPage
import tagging

from accounts.models      import UserProfile, UserKind, Position
from accounts.models      import ContactMethod, ContactItem
from announcements.models import Announcement
from articles.models      import Article, Section, Subsection, Format
from articles.models      import Special, SpecialsCategory, DummySpecialTarget
from comments.models      import PublicComment
from issues.models        import Issue, Menu, Weather, WeatherJoke, Event
from media.models         import ImageFile, MediaBucket
from polls.models         import Poll, Option
from jobs.models          import JobListing

### Site

Site.objects.all().delete()
site = Site.objects.create(name="The Daily Gazette", domain="daily.swarthmore.edu", pk=1)


### Flat Pages

about = site.flatpage_set.create(
    url="/about/",
    title="About Us",
    content="Yo, we're the Daily Gazette!"
)

policies = site.flatpage_set.create(
    url="/policies/",
    title="Policies",
    content="Don't suck, and we won't hate you."
)

contact = site.flatpage_set.create(
    url="/about/contact/",
    title="Contact Us",
    content="Email us at <span style=\"font-family: monospace;\">dailygazette at swarthmore dot edu</span>."
)

employment = site.flatpage_set.create(
    url="/join/",
    title="Employment",
    content="If you show up to meetings, or even if you don't, you can probably write for us."
)


### Groups

reader_group       = Group.objects.create(name="Readers")
reporter_group     = Group.objects.create(name="Reporters")
photographer_group = Group.objects.create(name="Photographers")
editor_group       = Group.objects.create(name="Editors")
admin_group        = Group.objects.create(name="Admins")

ct = ContentType.objects.get_for_model(PublicComment)

reader_group.permissions.add(
    Permission.objects.get(content_type=ct, codename='can_post_directly')
)

ab = Permission.objects.get(content_type=ct,codename='can_moderate_absolutely')
for g in (editor_group, admin_group):
    g.permissions.add(ab)

### Users

student = UserKind.objects.create(kind='s', year=2000)

cell_phone = ContactMethod.objects.create(name="Cell Phone")
aim        = ContactMethod.objects.create(name="AIM")
gtalk      = ContactMethod.objects.create(name="GTalk / Jabber")

def make_user(username, first, last, email=None, contact={}, bio=None, kind=student, groups=None):
    email = email or "%s@swarthmore.edu" % username
    user = User.objects.create_user(username, email)
    user.first_name = first
    user.last_name  = last
    if groups:
        user.groups = groups
    user.is_staff = True
    user.save()
    
    profile = UserProfile.objects.create(user=user, bio=bio, kind=kind)
    for method in contact:
        profile.contact_items.create(method=method, value=contact[method])
    
    return user

bob  = make_user('bob', 'Bob', 'Jones', 'bob@example.com',
                 {cell_phone:'123-456-7890', aim: 'bobjones52'},
                 groups=[reader_group, editor_group])
jack = make_user('jack', 'Jack', 'McSmith', 'jack@uppityup.com',
                 bio="I'm pretty much the man.",
                 groups=[reader_group, photographer_group, editor_group])
jill = make_user('jill', 'Jill', 'Carnegie', 'jill@thehill.com',
                 contact={gtalk: "jill@thehill.com"}, 
                 groups=[reader_group, admin_group])
bone = make_user('bone', 'The', 'Bone Doctress', 'doctress@example.com',
                 bio="I'm a mysterious figure.", 
                 groups=[reader_group, reporter_group])
angry = make_user('angry', 'Angry', 'Man', 'somedude@swat.net',
                 bio="I used to be in charge of this paper, but I've since moved "
                     "on to bigger and better things: complaining and nitpicking.",
                 groups=[reader_group])
angry.is_staff = False
angry.save()

zoe = make_user('zoe', 'Zoe', 'Davis', groups=[reader_group, reporter_group])
finlay = make_user('finlay', 'Finlay', 'Logan', groups=[reader_group, reporter_group])
neena = make_user('neena', 'Neena', 'Cherayil', groups=[reader_group, reporter_group])
lauren = make_user('lauren', 'Lauren', 'Stokes', groups=[reader_group, reporter_group])
brandon = make_user('brandon', 'Brandon', 'Lee Wolff', groups=[reader_group])

dougal = make_user('dougal', 'Dougal', 'Sutherland', 'dsuther1@swarthmore.edu', groups=[reader_group, admin_group])
dougal.password = 'sha1$8b8f9$e9526bcd787b71bc9fb1f68965815e2508333a6e'
dougal.is_superuser = True
dougal.save()

### Positions

reader          = Position.objects.create(name="Reader",             rank=0)
swat_reader     = Position.objects.create(name="Swarthmore Reader",  rank=1)
columnist       = Position.objects.create(name="Columnist",          rank=3)
guest_writer    = Position.objects.create(name="Guest Writer",       rank=4)
reporter        = Position.objects.create(name="Staff Reporter",     rank=5)
photographer    = Position.objects.create(name="Staff Photographer", rank=5)
tech_director   = Position.objects.create(name="Technical Director", rank=8,  is_editor=True)
news_editor     = Position.objects.create(name="News Editor",        rank=9,  is_editor=True)
arts_editor     = Position.objects.create(name="Arts Editor",        rank=9,  is_editor=True)
features_editor = Position.objects.create(name="Features Editor",    rank=9,  is_editor=True)
photo_editor    = Position.objects.create(name="Photography Editor", rank=9,  is_editor=True)
bossman         = Position.objects.create(name="Editor-In-Chief",    rank=10, is_editor=True)


### Users' having Positions
bob_p = bob.get_profile()
jack_p = jack.get_profile()
jill_p = jill.get_profile()
bone_p = bone.get_profile()
angry_p = angry.get_profile()

bob_p.add_position(reader,      date(2005, 9, 1), date(2006, 9, 1))
bob_p.add_position(reporter,    date(2006, 9, 1), date(2007, 9, 1))
bob_p.add_position(news_editor, date(2007, 9, 1))

jack_p.add_position(photographer, date(2006, 9, 1))
jack_p.add_position(photo_editor, date(2007, 12, 4))

jill_p.add_position(reporter,    date(2004, 9, 1), date(2005, 9, 1))
jill_p.add_position(arts_editor, date(2005, 9, 1), date(2006, 9, 1))
jill_p.add_position(bossman,     date(2006, 9, 1))

bone_p.add_position(reader,    date(2006, 9, 1))
bone_p.add_position(columnist, date(2008, 1, 21))

angry_p.add_position(bossman, date(2002, 9, 1), date(2006, 9, 1))
angry_p.add_position(reader,  date(2006, 9, 1))

p = lambda u: u.get_profile()

p(zoe).add_position(reporter)
p(finlay).add_position(reporter)
p(neena).add_position(reporter)
p(lauren).add_position(bossman)
p(brandon).add_position(guest_writer)

### Sections

sect = lambda n, s, d: Section.objects.create(name=n, slug=s, description=d)
sub = lambda p, n, s, d: Subsection.objects.create(name=n, slug=s, description=d, section=p)

news = sect("News", "news", "What's going on in the world.")
students = sub(news, "Students", "students", "Swarthmore students and their doings.")
facstaff = sub(news, "Faculty & Staff", "facstaff", "About Swarthmore faculty and staff.")
alumni = sub(news, "Alumni", "alumni", "The crazy world after Swarthmore.")

athletics = sect("Athletics", "athletics", "Swarthmore's athletes.")
features = sect("Features", "features", "The happenings around town.")
opinions = sect("Opinions", "opinions", "What people have to say.")

columns  = sect("Columns", "columns", "Foreign countries, sex, or both.")
bone_doctress = sub(columns, "The Bone Doctress", "bone_doctress", "Everyone's favorite sex column.")

### Formats
textile = Format.objects.create(name="Textile", function="textile")
html    = Format.objects.create(name="Raw HTML", function="html")


### Articles

nobody_loves_me = Article.objects.create(
    short_title="Nobody Loves Me",
    headline="Nobody Loves Me",
    subtitle="It's True: Not Like You Do",
    slug='no-love',
    section=columns,
    summary="The Bone Doctress takes a break from her usual witty recountings of "
            "sexual escapades to share with you the lyrics to a Portishead song.",
    short_summary="The Bone Doctress laments the lack of love in her life, by way of "
                  "Portishead lyrics.",
    format=textile,
    status='p',
    position='m',
    possible_position='m'
)
nobody_loves_me.add_author(bone_p)
nobody_loves_me.subsections.add(bone_doctress)
nobody_loves_me.text = """To pretend no one can find
The fallacies of morning rose
Forbidden fruit, hidden eyes
Curtises that I despise in me
Take a ride, take a shot now

Cos nobody loves me
Its true
Not like you do

Covered by the blind belief
That fantasies of sinful screens
Bear the facts, assume the dye
End the vows no need to lie, enjoy
Take a ride, take a shot now

Cos nobody loves me
Its true
Not like you do

Who oo am I, what and why
Cos all I have left is my memories of yesterday
Ohh these sour times

Cos nobody loves me
Its true
Not like you do

After time the bitter taste
Of innocence decent or race
Scattered seeds, buried lives
Mysteries of our disguise revolve
Circumstance will decide ....

Cos nobody loves me
Its true
Not like you do

Cos nobody loves me
Its true
Not like you
Nobody loves.. me
Its true
Not, like, you.. do"""
nobody_loves_me.revise_text( nobody_loves_me.text +  
  "\n\nSorry I forgot to cite! Hehe, no plagiarism plz. its by portishead, "
  "called nobody loves me or sour times or somethyng, off dummy i think. mebbe "
  "portishead. actually yeah i think its off theyr secund album. lawl. kkthx.")
nobody_loves_me.tags = "music"

bucket_o_bones = MediaBucket.objects.create(slug="bone-doctress")
nobody_loves_me.bucket = bucket_o_bones
nobody_loves_me.front_image = ImageFile.objects.create(slug="portishead",
                                    data="portishead.jpg",
                                    bucket=bucket_o_bones,
                                    shape='w')
nobody_loves_me.save()


scandal = Article.objects.create(
    headline="Al Bloom Pressured Out By Board of Managers",
    short_title="Al Bloom Forced Out By BoM",
    subtitle="Allegations of Involvement with Empereror's Club VIP Surface",
    slug="bloom-scandal",
    section=news,
    short_summary="Allegations have surfaced that Al Bloom was involved in the "
            "Emperor's Club VIP scandal.",
    summary="One member of the Board of Managers has allegedly accused Al Bloom "
            "of involvement with the Emperor's Club VIP, and has pictures to back "
            "it up. Some say this is related to his recent resignation.",
    long_summary="Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do "
                 "eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim "
                 "ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut "
                 "aliquip ex ea commodo consequat. Duis aute irure dolor in "
                 "reprehenderit in voluptate velit esse cillum dolore eu fugiat "
                 "nulla pariatur. Excepteur sint occaecat cupidatat non proident, "
                 "sunt in culpa qui officia deserunt mollit anim id est laborum.",
    text='<div class="imgLeft"><img src="bloom-walking-thumb" /></div>\n\n'
         "An investigation by the Gazette has uncovered connections between Al "
         "Bloom and the Emperor's Club VIP. Photos have surfaced that show him "
         "clearly engaging in unseemly acts with a woman who looks suspiciously "
         "like former New York governor Spitzer's pricey prostitute.\n\n"
         "A senior member of the Board of Managers, who refused to reveal his "
         "actual identity in the posting, supplied these photos to the community "
         "through an online forum and claimed that they were the true reason "
         "behind Al Bloom's unexpected retirement.\n\n "
         "The College and other Board members refused comment.\n\n"
         "Some students, however, have expressed concern that the photos may be "
         'fake: "I can tell by the pixels," claimed one rising senior, "and by '
         "having seen a few 'shops in my time.\"\n\n"
         "The Gazette will have more on this story as the story develops.\n\n"
         "[source: http://dailyjolt.com]",
    format=textile,
    status='p',
    pub_date=datetime.now() - timedelta(hours=3),
    position='t',
    possible_position='t'
)
scandal.add_author(bob_p, jack_p)
scandal.subsections.add(facstaff)
scandal.tags = "Al Bloom, Board of Managers, Daily Jolt"

scandal_pics = MediaBucket.objects.create(slug="bloom-scandal")
scandal.bucket = scandal_pics
scandal.thumbnail = ImageFile.objects.create(data="al-bloom-thumb.png", 
                                             slug="bloom-walking-thumb",
                                             bucket=scandal_pics,
                                             shape='t')
scandal.front_image = ImageFile.objects.create(data="al-bloom.jpg", 
                                               slug="bloom-walking", 
                                               bucket=scandal_pics,
                                               shape='w')
scandal.save()



scandal2 = Article.objects.create(
    headline="Al Bloom Pressured Out By Board of Managers",
    short_title="Al Bloom Forced Out By BoM",
    subtitle="Allegations of Involvement with Empereror's Club VIP Surface",
    slug="bloom-scandal-second",
    section=news,
    short_summary="Allegations have surfaced that Al Bloom was involved in the "
            "Emperor's Club VIP scandal2.",
    summary="One member of the Board of Managers has allegedly accused Al Bloom "
            "of involvement with the Emperor's Club VIP, and has pictures to back "
            "it up. Some say this is related to his recent resignation.",
    long_summary="Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do "
                 "eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim "
                 "ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut "
                 "aliquip ex ea commodo consequat. Duis aute irure dolor in "
                 "reprehenderit in voluptate velit esse cillum dolore eu fugiat "
                 "nulla pariatur. Excepteur sint occaecat cupidatat non proident, "
                 "sunt in culpa qui officia deserunt mollit anim id est laborum.",
    text='<div class="imgLeft"><img src="bloom-walking-thumb" /></div>\n\n'
         "An investigation by the Gazette has uncovered connections between Al "
         "Bloom and the Emperor's Club VIP. Photos have surfaced that show him "
         "clearly engaging in unseemly acts with a woman who looks suspiciously "
         "like former New York governor Spitzer's pricey prostitute.\n\n"
         "A senior member of the Board of Managers, who refused to reveal his "
         "actual identity in the posting, supplied these photos to the community "
         "through an online forum and claimed that they were the true reason "
         "behind Al Bloom's unexpected retirement.\n\n "
         "The College and other Board members refused comment.\n\n"
         "Some students, however, have expressed concern that the photos may be "
         'fake: "I can tell by the pixels," claimed one rising senior, "and by '
         "having seen a few 'shops in my time.\"\n\n"
         "The Gazette will have more on this story as the story develops.\n\n"
         "[source: http://dailyjolt.com]",
    format=textile,
    status='p',
    pub_date=datetime.now() - timedelta(hours=3),
    position='t',
    possible_position='t'
)
scandal2.add_author(bob_p, jack_p)
scandal2.subsections.add(facstaff)
scandal2.tags = "Al Bloom, Board of Managers, Daily Jolt"
scandal2.bucket = scandal_pics
scandal2.thumbnail = scandal.thumbnail
scandal2.front_image = scandal.front_image
scandal2.save()


boring = Article.objects.create(
    headline="Nothing Happened",
    subtitle="It's Summer: Did You Expect Something Else?",
    slug="boredom",
    section=news,
    summary="Absolutely nothing happened at all. It was quite boring. So boring, "
            "to be perfectly honest, I have not a thing to say about it. That's "
            "why the text of the story is all latin and crap.",
    text="Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod "
         "tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim "
         "veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea "
         "commodo consequat. Duis aute irure dolor in reprehenderit in voluptate "
         "velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint "
         "occaecat cupidatat non proident, sunt in culpa qui officia deserunt "
         "mollit anim id est laborum.\n\n"
         "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod "
         "tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim "
         "veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea "
         "commodo consequat. Duis aute irure dolor in reprehenderit in voluptate "
         "velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint "
         "occaecat cupidatat non proident, sunt in culpa qui officia deserunt "
         "mollit anim id est laborum.",
    format=textile,
    status='p',
    position='m',
    possible_position='m'
)
boring.add_author(jack_p)

internet_bucket = MediaBucket.objects.create(slug="internet")
boring.bucket = internet_bucket
boring.front_image = ImageFile.objects.create(slug="boring-baby",
                                              bucket = internet_bucket,
                                              data="boring.jpg",
                                              shape='t')
boring.save()

boring2 = Article.objects.create(
    headline="Nothing Happened",
    subtitle="It's Summer: Did You Expect Something Else?",
    slug="boring2",
    section=news,
    summary="Absolutely nothing happened at all. It was quite boring. So boring, "
            "to be perfectly honest, I have not a thing to say about it. That's "
            "why the text of the story is all latin and crap.",
    text="Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod "
         "tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim "
         "veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea "
         "commodo consequat. Duis aute irure dolor in reprehenderit in voluptate "
         "velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint "
         "occaecat cupidatat non proident, sunt in culpa qui officia deserunt "
         "mollit anim id est laborum.\n\n"
         "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod "
         "tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim "
         "veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea "
         "commodo consequat. Duis aute irure dolor in reprehenderit in voluptate "
         "velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint "
         "occaecat cupidatat non proident, sunt in culpa qui officia deserunt "
         "mollit anim id est laborum.",
    format=textile,
    status='p',
    position='m',
    possible_position='m'
)
boring2.add_author(jack_p)
boring2.bucket = internet_bucket
boring2.front_image = boring.front_image
boring2.save()


boring3 = Article.objects.create(
    headline="Nothing Happened",
    subtitle="It's Summer: Did You Expect Something Else?",
    slug="boring3",
    section=news,
    summary="Absolutely nothing happened at all. It was quite boring. So boring, "
            "to be perfectly honest, I have not a thing to say about it. That's "
            "why the text of the story is all latin and crap.",
    text="Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod "
         "tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim "
         "veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea "
         "commodo consequat. Duis aute irure dolor in reprehenderit in voluptate "
         "velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint "
         "occaecat cupidatat non proident, sunt in culpa qui officia deserunt "
         "mollit anim id est laborum.\n\n"
         "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod "
         "tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim "
         "veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea "
         "commodo consequat. Duis aute irure dolor in reprehenderit in voluptate "
         "velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint "
         "occaecat cupidatat non proident, sunt in culpa qui officia deserunt "
         "mollit anim id est laborum.",
    format=textile,
    status='p',
    position='m',
    possible_position='m'
)
boring3.add_author(jack_p)
boring3.bucket = internet_bucket
boring3.front_image = boring.front_image
boring3.save()


boring4 = Article.objects.create(
    headline="Nothing Happened",
    subtitle="It's Summer: Did You Expect Something Else?",
    slug="boring4",
    section=news,
    summary="Absolutely nothing happened at all. It was quite boring. So boring, "
            "to be perfectly honest, I have not a thing to say about it. That's "
            "why the text of the story is all latin and crap.",
    text="Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod "
         "tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim "
         "veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea "
         "commodo consequat. Duis aute irure dolor in reprehenderit in voluptate "
         "velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint "
         "occaecat cupidatat non proident, sunt in culpa qui officia deserunt "
         "mollit anim id est laborum.\n\n"
         "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod "
         "tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim "
         "veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea "
         "commodo consequat. Duis aute irure dolor in reprehenderit in voluptate "
         "velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint "
         "occaecat cupidatat non proident, sunt in culpa qui officia deserunt "
         "mollit anim id est laborum.",
    format=textile,
    status='p',
    position='m',
    possible_position='m'
)
boring4.add_author(jack_p)
boring4.bucket = internet_bucket
boring4.front_image = boring.front_image
boring4.save()

def art(author, subsection=None, **keywords):
    keywords.setdefault('format', textile)
    keywords.setdefault('status', 'p')
    keywords.setdefault('position', 'n')
    keywords.setdefault('possible_position', 'n')
    if subsection:
        keywords.setdefault('section', subsection.section)
    article = Article.objects.create(**keywords)
    article.add_author(p(author))
    if subsection:
        article.subsections.add(subsection)
    article.save()
    return article

school = art(
    headline="Project Shingayi Plans to Construct Zimbabwean School",
    slug="project-shingayi",
    subsection=students,
    summary="Yay African schools lah lah lah.",
    text="whoa",
    author=zoe
)

poker = art(
    headline="Swat Alums Turn Poker Pros",
    slug="poker-pros",
    subsection=alumni,
    summary="Maybe the coolest thing ever.",
    text="double whoa",
    author=finlay
)

paces = art(
    headline="The History Of Paces' Mural",
    slug="paces-mural",
    section=features,
    summary="It was painted by some dude.",
    text="yah",
    author=neena
)

tarble = art(
    headline="Major Changes Planned For Tarble",
    slug="tarble-changes",
    section=news,
    summary="They be changin' stuff, yo.",
    text="",
    author=finlay
)

denglish = Subsection.objects.create(name='Honors Denglish',
                                     slug='honors-denglish',
                                     section=columns)
nestbeschmutzer = art(
    headline="<i>Nestbeschmutzer</i>, Now Out of Austria",
    slug="nestbeschmutzer",
    subsection=denglish,
    summary="whoa. german.",
    text="",
    author=lauren
)

facebook = art(
    headline="Under Reporting? Facebook at Swarthmore",
    short_title="Under Reporting? Swat Facebook Use",
    slug="facebook",
    subsection=students,
    summary="People use it, probably more than they admit to.",
    text="Stat 11 <3",
    author=brandon
)

def random_art(num):
    sec = random.choice(list(Section.objects.all()))
    sub = random.choice(list(sec.subsections.all()) + [None])
    sec_name = sub.name if sub else sec.name
    return art(
        headline="%s article #%d" % (sec_name, num),
        slug="num_%d" % num,
        section=sec,
        subsection=sub,
        summary="Random article #%d in %s" % (num, sec_name),
        text=("%s! " % sec_name) * 10,
        author=brandon,
        pub_date=datetime.now() - timedelta(days=2)
    )

randoms = [random_art(n) for n in range(100)]

### Comments

PublicComment.objects.new(
    subject=scandal,
    name="Concerned",
    email='no@no.com',
    text="First the Haverford president, then the Bryn Mawr president, "
         "then the Swat president, one per year? Something more is "
         "going on than just prostitution scandals!",
    time=datetime.now() - timedelta(hours=2, minutes=4),
    check_spam=False,
    pre_approved=True
)

PublicComment.objects.new(
    subject=scandal,
    user=jack.get_profile(),
    text="You're crazy, Concerned. Nothing's going on!",
    time=datetime.now() - timedelta(hours=1, minutes=8)
)

PublicComment.objects.new(
    subject=scandal,
    user=jack.get_profile(),
    name="Whoa",
    text="#1 is so right. I bet Jack McSmith figured it out the real "
         "conspiracy but doesn't want to expose it, because the conspirators "
         "have his baby daughter held hostage or something.",
    time=datetime.now() - timedelta(hours=1, minutes=7),
    pre_approved=True,
    check_spam=False
)

PublicComment.objects.new(
    subject=scandal,
    user=jill.get_profile(),
    text="Our baby is being held hostage, Jack? I thought she was at your mom's!",
    time=datetime.now() - timedelta(minutes=2)
)

offensive = PublicComment.objects.new(
    subject=scandal,
    user=angry.get_profile(),
    text="Lol! Typical of the trash on the Gazette!<br/><br/>At least since I left, that is. Back in the day, when I was running the Gazette single-handedly, I researched each and every article for a minimum of sixteen hours, getting quotes from at least nine different sources in the process. THAT's the only way to guarantee objectivity. And it happened like that for EVERY article. Even the weather. Not getting enough sources is a slippery slope, one the Gazette has begun to sled down on one of those new-fangled plastic sleds that go really really fast. You suck, Jack McSmith!",
    time=datetime.now() - timedelta(minutes=1, seconds=30)
)

PublicComment.objects.new(
    subject=scandal,
    ip_address='130.58.9.13',
    email='hi@there.com',
    name="Bob",
    text="What are you talking about, #5? This is quality investigative journalism at its finest.",
    time=datetime.now(),
    check_spam=False
)

offensive.add_vote(positive=False, user=jill.get_profile())

### Announcements

Announcement.objects.create(
    kind='s', 
    slug="summer-return",
    text="We're up and publishing for a very special summer term! This is a "
         "very special term, though, so only a select handful get to read us "
         "right now...or ever.",
    date_end = date.today() + timedelta(days=1)
)

Announcement.objects.create(
    kind='c',
    slug="cookies",
    date_end = date.today() + timedelta(days=10),
    sponsor="Summer Cookie Fairies",
    title="There Will Be Cookies",
    text="There will be cookies in each and every cabinet across campus, "
         "courtesy of the Summer Cookie Fairies. Get them while they last!",
    is_published=True
)

Announcement.objects.create(
    kind='c',
    slug='games',
    date_end=date.today() + timedelta(days=2),
    sponsor="SCCS",
    sponsor_url="http://sccs.swarthmore.edu/",
    title="There Will Be Games",
    event_place="SCCS Lounge",
    event_date=date.today() + timedelta(days=2),
    event_time="7pm",
    text="Come play games with us, and stuff.",
    is_published=True
)

Announcement.objects.create(
    kind='c',
    slug='blood',
    date_end=date.today() + timedelta(days=3),
    sponsor='Movie Commitee',
    title='There Will Be Blood',
    event_place='Sci 101',
    event_date=date.today() + timedelta(days=3),
    event_time="7 and 9 pm",
    is_published=True
)

### Polls

jolt_poll = Poll.objects.create(
    name = "Is the Daily Jolt a legitimate news source?",
    slug = "is-jolt-legit",
    question = "We got most (read: all) of our information from this article "
               "from the Daily Jolt. Is that okay?",
    allow_anon = True,
    article = scandal
)

jolt_yes   = Option.objects.create(name="yes", poll=jolt_poll,
    description = "Absolutely. Don't you know that's where CNN gets its news?")
jolt_no    = Option.objects.create(name="no",  poll=jolt_poll,
    description = "No way. Don't you know that's where CNN gets its news?")
jolt_maybe = Option.objects.create(name="maybe", poll=jolt_poll,
    description = "Critical thinking is hard. Let's go shopping!")

jolt_poll.vote(bob, jolt_yes)
jolt_poll.vote(jack, jolt_yes)
jolt_poll.vote(jill, jolt_no)
jolt_poll.vote(bone, jolt_maybe)


### Issues

try:
    menu = Menu.objects.for_today()
except:
    menu = Menu.objects.create(closed=True, message="Sharples is closed, sucka!")

try:
    weather = Weather.objects.for_today()
except:
    weather = Weather.objects.create(
        today = "Very happy. High of 234.",
        tonight = "Very sad. Low of 12.",
        tomorrow = "Chance of euphoria. High of 68."
    )

try:
    Event.objects.update(forward=timedelta(days=20))
except:
    Event.objects.create(name="Random ITS Thing", start_day=date.today(), end_day=date.today(), link="http://calendar.swarthmore.edu/calendar/EventList.aspx?view=EventDetails&eventidn=3270&information_id=10375&type=")
    Event.objects.create(name="Other ITS Thing", start_day=date.today(), start_time=time(12), end_day=date.today(), end_time=time(14), link="http://calendar.swarthmore.edu/calendar/EventList.aspx?view=EventDetails&eventidn=3271&information_id=10378&type=")
    Event.objects.create(name="Running ITS Thing", start_day=date.today(), end_day=date.today()+timedelta(days=5), link="http://calendar.swarthmore.edu/calendar/EventList.aspx?fromdate=8/27/2008&todate=8/27/2008&display=Day&type=public&eventidn=3097&view=EventDetails&information_id=9573")

joke = WeatherJoke.objects.create(
    line_one = "I don't like writing weather jokes, most of the time.",
    line_two = "And nobody's going to complain if there isn't one here.",
    line_three = "So why would I bother to write a real one?"
)

issue_today = Issue.objects.create(menu=menu, weather=weather, joke=joke)

issue_today.add_article(scandal)
issue_today.add_article(nobody_loves_me)
issue_today.add_article(boring)
issue_today.add_article(tarble)
issue_today.add_article(paces)
issue_today.add_article(nestbeschmutzer)

### Specials

rand = MediaBucket.objects.create(slug="random")
fake_target = DummySpecialTarget.objects.create(url="http://google.com")

nestbesch = Special.objects.create(
    title="<em>Nestbeschmutzer</em> Now Out Of Austria",
    target=nestbeschmutzer,
    category=SpecialsCategory.objects.create(name="Columns"),
    image=ImageFile.objects.create(bucket=rand, 
                                   slug="tunnel", 
                                   data="specials/austria.png",
                                   name="Crazy Austrian Tunnel")
)

arts = Special.objects.create(
    title="Senior Arts Exhibits",
    target=fake_target,
    category= SpecialsCategory.objects.create(name="Arts"),
    image=ImageFile.objects.create(bucket=rand,
                                   slug="artistry",
                                   data="specials/senior-art.png",
                                   name="Some Senior Art")
)

blue_tree = Special.objects.create(
    title="What Happened To The Blue Tree?",
    target=paces,
    category=SpecialsCategory.objects.create(name="Ask The Gazette"),
    image=ImageFile.objects.create(bucket=rand,
                                   slug="blue-tree",
                                   data="specials/atg-blue-tree.png",
                                   name="The Blue Tree")
)

zagette = Special.objects.create(
    title="The Gazette's Zagette Goes Live!",
    target=fake_target,
    category=SpecialsCategory.objects.create(name="Specials"),
    image=ImageFile.objects.create(bucket=rand,
                                   slug="zagette",
                                   data="specials/dining.png",
                                   name="Dining")
)

hiring = Special.objects.create(
    title="The Gazette Is Hiring",
    target=fake_target,
    category=SpecialsCategory.objects.create(name="Gazette News"),
    image=ImageFile.objects.create(bucket=rand,
                                   slug="hiring",
                                   data="specials/hiring.png",
                                   name="Reportin' 'n Stuff")
)


### Jobs

kids = JobListing.objects.create(
    name="Volunteer with Chester Children",
    slug='chester-kids',
    pub_date=date(2008, 5, 10),
    is_filled=False,
    is_paid=False,
    hours="9-3, Tues-Wed-Thurs",
    when="July 7 - August 7",
    where="Nia Center, Chester, PA",
    at_swat=False,
    needs_car=False,
    description="Volunteers needed to help with an arts and "
"academics camp held from 9am-3pm, Tues-Wed-Thurs from July 7-August 7. "
"If you are planning to be in the area and have some free time (any help "
"would be great, even just one day a week or part days) this will be a lot "
" of fun! The children are K-5th grade and will be working on reading, "
"math, an art for peace project, and other fun activities like going to the "
"park/pool or fieldtrips.\n"
"If you are interested and available, please contact Lauren Yoshizawa '09 "
"(lyoshiz1) to get more information."
)

publications = JobListing.objects.create(
    name="Publications Intern",
    slug='publications-intern',
    pub_date=date(2008, 4, 22),
    is_filled=False,
    is_paid=True,
    pay="$8.56/hr",
    hours="12/wk",
    when="Summer",
    where="Publications Office",
    at_swat=True,
    needs_car=False,
    description="Publications Office Needs Summer Student Worker. Conscientious, organized, and reliable student with an eye for accuracy needed to work in the Publications Office up to 12 hours per week during the summer. Work will include among other duties, fact checking copy using College database, Internet, and other resources; proofreading; and compiling mailing packets for Class Notes secretaries. Successful candidate must have good writing, grammar, and spelling skills, and be computer savvy. Familiarity with AP and Chicago style is a plus. Position could continue into academic year. Salary: $8.56 per hour. Please contact Susan Breen at ext. 8579 or submit resume including specific qualifications for this position to sbreen1@swarthmore.edu by April 30."
)

its = JobListing.objects.create(
    name="ITS Web Intern",
    slug='its-web-intern',
    pub_date=date(2008, 4, 30),
    is_filled=False,
    is_paid=False,
    hours="Negotiable",
    when="Summer",
    where="ITS",
    at_swat=True,
    needs_car=False,
    description="Do some stuff. More at http://www.swarthmore.edu/webintern.xml ."
)
