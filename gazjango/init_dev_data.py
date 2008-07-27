#!/usr/bin/env python

import settings
from django.core.management import setup_environ
setup_environ(settings)

### imports

from datetime import date, timedelta

from django.contrib.auth.models      import User, Group
from django.contrib.sites.models     import Site
from django.contrib.flatpages.models import FlatPage
import tagging

from accounts.models      import UserProfile, Position
from announcements.models import Announcement
from articles.models      import Article, Category, Format
from articles.models      import Special, SpecialsCategory, DummySpecialTarget
from issues.models        import Issue, Menu, Weather, WeatherJoke
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


### Users

def make_user(username, first, last, email=None, phone=None, contact=None, bio=None, groups=None):
    email = email or "%s@swarthmore.edu" % username
    user = User.objects.create_user(username, email)
    user.userprofile_set.add(UserProfile(phone=phone, contact=contact, bio=bio))
    user.first_name = first
    user.last_name  = last
    if groups:
        user.groups = groups
    user.save()
    return user

bob  = make_user('bob', 'Bob', 'Jones', 'bob@example.com',
                 '123-456-7890', 'AIM: bobjones52',
                 groups=[reader_group, editor_group])
jack = make_user('jack', 'Jack', 'McSmith', 'jack@uppityup.com',
                 bio="I'm pretty much the man.",
                 groups=[reader_group, photographer_group, editor_group])
jill = make_user('jill', 'Jill', 'Carnegie', 'jill@thehill.com',
                 contact="GTalk: jill@thehill.com", 
                 groups=[reader_group, admin_group])
bone = make_user('bone', 'The', 'Bone Doctress', 'doctress@example.com',
                 bio="I'm a mysterious figure.", 
                 groups=[reader_group, reporter_group])
angry = make_user('angry', 'Angry', 'Man', 'somedude@swat.net',
                 bio="I used to be in charge of this paper, but I've since moved "
                     "on to bigger and better things: complaining and nitpicking.",
                 groups=[reader_group])
zoe = make_user('zoe', 'Zoe', 'Davis', groups=[reader_group, reporter_group])
finlay = make_user('finlay', 'Finlay', 'Logan', groups=[reader_group, reporter_group])
neena = make_user('neena', 'Neena', 'Cherayil', groups=[reader_group, reporter_group])
lauren = make_user('lauren', 'Lauren', 'Stokes', groups=[reader_group, reporter_group])
brandon = make_user('brandon', 'Brandon', 'Lee Wolff', groups=[reader_group])

### Positions

reader          = Position.objects.create(name="Reader",             rank=0)
swat_reader     = Position.objects.create(name="Swarthmore Reader",  rank=1)
columnist       = Position.objects.create(name="Columnist",          rank=3)
guest_writer    = Position.objects.create(name="Guest Writer",       rank=4)
reporter        = Position.objects.create(name="Staff Reporter",     rank=5)
photographer    = Position.objects.create(name="Staff Photographer", rank=5)
tech_director   = Position.objects.create(name="Technical Director", rank=8)
news_editor     = Position.objects.create(name="News Editor",        rank=9)
arts_editor     = Position.objects.create(name="Arts Editor",        rank=9)
features_editor = Position.objects.create(name="Features Editor",    rank=9)
photo_editor    = Position.objects.create(name="Photography Editor", rank=9)
bossman         = Position.objects.create(name="Editor-In-Chief",    rank=10)


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

### Categories

def cat(name, slug, description, parent=None):
    args = { 'name': name, 'slug': slug, 'description': description }
    if parent:
        args['parent'] = parent
    return Category.objects.create(**args)


news = cat("News", "news", "What's going on in the world.")
students = cat("Students", "students", "Swarthmore students and their doings.", news)
facstaff = cat("Faculty & Staff", "facstaff", "About Swarthmore faculty and staff.", news)
alumni = cat("Alumni", "alumni", "The crazy world after Swarthmore.", news)

features = cat("Features", "features", "The happenings around town.")
opinions = cat("Opinions", "opinions", "What people have to say.")

columns  = cat("Columns", "columns", "Foreign countries, sex, or both.")
bone_doctress = cat("The Bone Doctress", "bone_doctress", 
                    "Everyone's favorite sex column.", columns)

### Formats
textile = Format.objects.create(name="Textile", function="textile")
html    = Format.objects.create(name="Raw HTML", function="html")


### Articles

nobody_loves_me = Article.objects.create(
    short_title="Nobody Loves Me",
    headline="Nobody Loves Me",
    subtitle="It's True: Not Like You Do",
    slug='no-love',
    category=bone_doctress,
    summary="The Bone Doctress takes a break from her usual witty recountings of "
            "sexual escapades to share with you the lyrics to a Portishead song.",
    short_summary="The Bone Doctress laments the lack of love in her life, by way of "
                  "Portishead lyrics.",
    format=textile,
    status='p',
    position=2
)
nobody_loves_me.authors.add(bone_p)
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
                                    data="uploads/portishead.jpg",
                                    bucket=bucket_o_bones,
                                    shape='w')
nobody_loves_me.save()


scandal = Article.objects.create(
    headline="Al Bloom Pressured Out By Board of Managers",
    short_title="Al Bloom Forced Out By BoM",
    subtitle="Allegations of Involvement with Empereror's Club VIP Surface",
    slug="bloom-scandal",
    category=facstaff,
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
    position=1
)
scandal.authors.add(bob_p, jack_p)
scandal.tags = "Al Bloom, Board of Managers, Daily Jolt"

scandal_pics = MediaBucket.objects.create(slug="bloom-scandal")
scandal.bucket = scandal_pics
scandal.thumbnail = ImageFile.objects.create(data="uploads/al-bloom-thumb.png", 
                                             slug="bloom-walking-thumb",
                                             bucket=scandal_pics,
                                             shape='t')
scandal.front_image = ImageFile.objects.create(data="uploads/al-bloom.jpg", 
                                               slug="bloom-walking", 
                                               bucket=scandal_pics,
                                               shape='w')
scandal.save()


boring = Article.objects.create(
    headline="Nothing Happened",
    subtitle="It's Summer: Did You Expect Something Else?",
    slug="boredom",
    category=news,
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
    position=2
)
boring.authors.add(jack_p)

internet_bucket = MediaBucket.objects.create(slug="internet")
boring.bucket = internet_bucket
boring.front_image = ImageFile.objects.create(slug="boring-baby",
                                              bucket = internet_bucket,
                                              data="uploads/boring.jpg",
                                              shape='t')
boring.save()


def art(author, **keywords):
    keywords.setdefault('format', textile)
    keywords.setdefault('status', 'p')
    article = Article.objects.create(**keywords)
    article.authors.add(p(author))
    article.save()
    return article

school = art(
    headline="Project Shingayi Plans to Construct Zimbabwean School",
    slug="project-shingayi",
    category=students,
    summary="Yay African schools lah lah lah.",
    text="whoa",
    author=zoe
)

poker = art(
    headline="Swat Alums Turn Poker Pros",
    slug="poker-pros",
    category=alumni,
    summary="Maybe the coolest thing ever.",
    text="double whoa",
    author=finlay
)

paces = art(
    headline="The History Of Paces' Mural",
    slug="paces-mural",
    category=features,
    summary="It was painted by some dude.",
    text="yah",
    author=neena
)

tarble = art(
    headline="Major Changes Planned For Tarble",
    slug="tarble-changes",
    category=news,
    summary="They be changin' stuff, yo.",
    text="",
    author=finlay
)

nestbeschmutzer = art(
    headline="<i>Nestbeschmutzer</i>, Now Out of Austria",
    slug="nestbeschmutzer",
    category=columns,
    summary="whoa. german.",
    text="",
    author=lauren
)

facebook = art(
    headline="Under Reporting? Facebook at Swarthmore",
    short_title="Under Reporting? Swat Facebook Use",
    slug="facebook",
    category=students,
    summary="People use it, probably more than they admit to.",
    text="Stat 11 <3",
    author=brandon
)

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

issue_today = Issue.objects.create(
    menu = Menu.objects.create(closed=True, message="Sharples is closed, sucka!"),
    weather = Weather.objects.create(
        today = "Very happy. High of 234.",
        tonight = "Very sad. Low of 12.",
        tomorrow = "Chance of euphoria. High of 68."
    ),
    joke = WeatherJoke.objects.create(
        line_one = "I don't like writing weather jokes, most of the time.",
        line_two = "And nobody's going to complain if there isn't one here.",
        line_three = "So why would I bother to write a real one?"
    ),
    events = "Nothing's happening."
)
issue_today.add_article(scandal)
issue_today.add_article(nobody_loves_me)
issue_today.add_article(boring)


### Specials

rand = MediaBucket.objects.create(slug="random")
fake_target = DummySpecialTarget.objects.create(url="http://google.com")

nestbesch = Special.objects.create(
    title="<em>Nestbeschmutzer</em> Now Out Of Austria",
    target=nestbeschmutzer,
    category=SpecialsCategory.objects.create(name="Columns"),
    image=ImageFile.objects.create(bucket=rand, 
                                   slug="tunnel", 
                                   data="uploads/specials/austria.png",
                                   name="Crazy Austrian Tunnel")
)

arts = Special.objects.create(
    title="Senior Arts Exhibits",
    target=fake_target,
    category= SpecialsCategory.objects.create(name="Arts"),
    image=ImageFile.objects.create(bucket=rand,
                                   slug="artistry",
                                   data="uploads/specials/senior-art.png",
                                   name="Some Senior Art")
)

blue_tree = Special.objects.create(
    title="What Happened To The Blue Tree? (aka the Paces mural)",
    target=paces,
    category=SpecialsCategory.objects.create(name="Ask The Gazette"),
    image=ImageFile.objects.create(bucket=rand,
                                   slug="blue-tree",
                                   data="uploads/specials/atg-blue-tree.png",
                                   name="The Blue Tree")
)

zagette = Special.objects.create(
    title="The Gazette's Zagette Goes Live!",
    target=fake_target,
    category=SpecialsCategory.objects.create(name="Specials"),
    image=ImageFile.objects.create(bucket=rand,
                                   slug="zagette",
                                   data="uploads/specials/dining.png",
                                   name="Dining")
)

hiring = Special.objects.create(
    title="The Gazette Is Hiring",
    target=fake_target,
    category=SpecialsCategory.objects.create(name="Gazette News"),
    image=ImageFile.objects.create(bucket=rand,
                                   slug="hiring",
                                   data="uploads/specials/hiring.png",
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
