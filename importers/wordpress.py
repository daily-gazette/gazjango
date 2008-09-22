#!/usr/bin/env python

import MySQLdb as db
from optparse import OptionParser
import os,sys,re

sys.path.append("..")
sys.path.append("../gazjango")

import settings
import django.core.management
django.core.management.setup_environ(settings)

import datetime
from django.contrib.auth.models         import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models        import Site
from django.contrib.flatpages.models    import FlatPage
from gazjango import tagging

from gazjango.accounts.models      import UserProfile, UserKind, Position
from gazjango.accounts.models      import ContactMethod, ContactItem
from gazjango.announcements.models import Announcement
from gazjango.articles.models      import Article, PhotoSpread, Format
from gazjango.articles.models      import Section, Subsection
from gazjango.articles.models      import Special, SpecialsCategory, DummySpecialTarget
from gazjango.comments.models      import PublicComment
from gazjango.issues.models        import Issue, Menu, Weather, WeatherJoke, Event
from gazjango.media.models         import MediaFile, ImageFile, MediaBucket
from gazjango.polls.models         import Poll, Option
from gazjango.jobs.models          import JobListing

from collections import defaultdict


# =======================
# = Database Connection =
# =======================

parser = OptionParser()
parser.add_option("-H", "--host",     dest="host",   help="connect to HOST",      metavar="HOST",   default="localhost")
parser.add_option("-u", "--user",     dest="user",   help="authenticate as USER", metavar="USER",   default="root")
parser.add_option("-p", "--passwd",   dest="passwd", help="using PASSWD",         metavar="PASSWD", default="")
parser.add_option("-d", "--database", dest="db",     help="use database DB",      metavar="DB",     default="gazette_daily")
(options, args) = parser.parse_args()

if options.passwd == '-':
    print "db password: ",
    password = raw_input()
else:
    password = options.passwd

print "connecting to the old db..."
conn = db.connect(
    host=options.host,
    user=options.user,
    passwd=password,
    db=options.db
)

cursor = conn.cursor()

# ==========================
# = Flush the Old Database =
# ==========================

print "flushing database..."
u = django.core.management.ManagementUtility(['fakery', 'flush', '--noinput'])
u.execute()

# ========
# = Site =
# ========
print "making site object..."

Site.objects.all().delete()
site = Site.objects.create(name="The Daily Gazette", domain="daily.swarthmore.edu", pk=1)


# =========
# = Pages =
# =========
print "making static pages..."

about = site.page_set.create(
    url="/about/",
    title="About Us",
    content="Yo, we're the Daily Gazette!"
)

policies = site.page_set.create(
    url="/policies/",
    title="Policies",
    content="Don't suck, and we won't hate you."
)

contact = site.page_set.create(
    url="/about/contact/",
    title="Contact Us",
    content="Email us at <span style=\"font-family: monospace;\">dailygazette at swarthmore dot edu</span>.",
    parent=about
)

employment = site.page_set.create(
    url="/join/",
    title="Employment",
    content="If you show up to meetings, or even if you don't, you can probably write for us."
)


# ==========
# = Groups =
# ==========
print "making user groups..."

reader_group       = Group.objects.create(name="Readers")
ex_staff_group     = Group.objects.create(name="Ex-Staff")
reporter_group     = Group.objects.create(name="Reporters")
photographer_group = Group.objects.create(name="Photographers")
copy_editor_group  = Group.objects.create(name="Copy Editors")
editor_group       = Group.objects.create(name="Editors")
admin_group        = Group.objects.create(name="Admins")

ct = ContentType.objects.get_for_model(PublicComment)

reader_group.permissions.add(
    Permission.objects.get(content_type=ct, codename='can_post_directly')
)

ab = Permission.objects.get(content_type=ct,codename='can_moderate_absolutely')
for g in (editor_group, admin_group):
    g.permissions.add(ab)



# ==============
# = User Kinds =
# ==============
print "making user kinds..."

generic_student = UserKind.objects.create(kind='s')
generic_alum    = UserKind.objects.create(kind='a')
faculty_staff   = UserKind.objects.create(kind='f')
parent          = UserKind.objects.create(kind='p')
spec            = UserKind.objects.create(kind='k')
other           = UserKind.objects.create(kind='o')


# =============
# = Positions =
# =============

print "making positions..."
# we'll need to manually assign these
reader          = Position.objects.create(name="Reader",             rank=0)
swat_reader     = Position.objects.create(name="Swarthmore Reader",  rank=1)
columnist       = Position.objects.create(name="Columnist",          rank=4)
guest_writer    = Position.objects.create(name="Guest Writer",       rank=4)
reporter        = Position.objects.create(name="Staff Reporter",     rank=5)
photographer    = Position.objects.create(name="Staff Photographer", rank=5)
tech_director   = Position.objects.create(name="Technical Director", rank=8,  is_editor=True)
news_editor     = Position.objects.create(name="News Editor",        rank=9,  is_editor=True)
arts_editor     = Position.objects.create(name="Arts Editor",        rank=9,  is_editor=True)
features_editor = Position.objects.create(name="Features Editor",    rank=9,  is_editor=True)
photo_editor    = Position.objects.create(name="Photography Editor", rank=9,  is_editor=True)
editor_in_chief = Position.objects.create(name="Editor-In-Chief",    rank=10, is_editor=True)


# ===================
# = Contact Methods =
# ===================

print "making contact methods..."

cell  = ContactMethod.objects.create(name="Cell Phone")
phone = ContactMethod.objects.create(name="Phone")
yim   = ContactMethod.objects.create(name="Yahoo")
aim   = ContactMethod.objects.create(name="AIM")
gtalk = ContactMethod.objects.create(name="GTalk / Jabber")
msn   = ContactMethod.objects.create(name="MSN")


# =========
# = Users =
# =========

print "importing users..."

staff_groups = set([reporter_group, photographer_group, copy_editor_group,
                    editor_group, admin_group])

users = {}
cursor.execute("SELECT ID, user_nicename, user_email, display_name FROM gazette_users")
while True:
    row = cursor.fetchone()
    if row is None:
        break
    old_id, username, email, display_name = row
    
    users[int(old_id)] = defaultdict(lambda:"",
                                     username=username,
                                     email=email,
                                     display_name=display_name
                                     )

cursor.execute("SELECT user_id, meta_key, meta_value FROM gazette_usermeta WHERE NOT meta_key IN" \
               "('rich_editing', 'admin_color', 'closedpostboxes_post', 'gazette_autosave_draft_ids')")
capabilities_regex = re.compile(r's:\d+:\"(?P<id>\w+)\";b:1;')
while True:
    row = cursor.fetchone()
    if row is None:
        break
    old_id, key, val = row
    if key == "gazette_capabilities":
        val = capabilities_regex.findall(val)
    users[old_id][key] = val

for id in users:
    u = users[id]
    groups = []
    caps = u["gazette_capabilities"]
    if "administrator" in caps:
        groups.append(admin_group)
    if "reader" in caps:
        groups.append(reader_group)
    if "reporter" in caps or "reporters" in caps:
        groups.append(reporter_group)
    if "photographer" in caps:
        groups.append(photographer_group)
    if "editor" in caps:
        groups.append(editor_group)
    if "old_writers" in caps:
        groups.append(ex_staff_group)
    
    new_user = User.objects.create_user(u['username'], u['email'])
    if u['first_name'] or u['last_name']:
        new_user.first_name = u['first_name']
        new_user.last_name  = u['last_name']
    else:
        split = u['display_name'].split(None, 1)
        if len(split) == 1:
            split += ['']
        new_user.first_name, new_user.last_name = split
    new_user.is_staff = bool(set(groups).intersection(staff_groups))
    new_user.groups = groups
    new_user.save()
    
    profile = UserProfile.objects.create(
        user=new_user,
        bio=u['description'], 
        kind=generic_student
    )
    
    for name, method in (('aim', aim), ('jabber', gtalk), ('yim', yim)):
        if name in u:
            profile.contact_items.create(method=method, value=u[name])
    
    u["new_id"] = new_user.id


# ============
# = Sections =
# ============

print "making sections..."

sec = lambda n, s, d, x=False: Section.objects.create(name=n, slug=s, description=d, is_special=x)
sub = lambda p, n, s, d: Subsection.objects.create(section=p, name=n, slug=s, description=d)

news = sec("News", "news", "What's going on in the world.")
students = sub(news, "Students",        "students", "Swarthmore students and their exploits.")
facstaff = sub(news, "Faculty & Staff", "facstaff", "About Swarthmore faculty and staff.")
alumni   = sub(news, "Alumni",          "alumni",   "What ex-Swarthmore students go on to do.")

features = sec("Features", "features", "The happenings around town.")
atg     = sub(features, "Ask the Gazette", "atg",             "The Gazette answers the questions you have.")
roundup = sub(features, "Weekend Roundup", "weekend-roundup", "What's going on each weekend.")

athletics = sec("Athletics", "sports", "Swarthmore's athletes.")
opinions_and_columns = sec("Opinions & Columns", "opinions", "What the community has to say.")
multimedia = sec("Multimedia", "multimedia", "Pictures and videos.")

misc = sec("Miscellaneous", "misc", "Miscellaneous things.")
platforms = sub(features, "Student Council Platforms", "stuco-platforms", "Platforms for student council elections.")


# ===========
# = Formats =
# ===========

print "making formats..."

html    = Format.objects.create(name="Raw HTML", function="html")
textile = Format.objects.create(name="Textile",  function="textile")


# ========
# = Tags =
# ========

print "making tags..."

special = tagging.models.TagGroup.objects.create(name="*Specials*")
orgs    = tagging.models.TagGroup.objects.create(name="Organizations")
depts   = tagging.models.TagGroup.objects.create(name="Departments")
places  = tagging.models.TagGroup.objects.create(name="Places")
people  = tagging.models.TagGroup.objects.create(name="People")

arts = special.tags.create(name="Living & Arts")

os = ("Amnesty International", "Anime & Manga Club", "ARC", "Ballroom & Swing Club", "Boy Meets Tractor", "Cantatrix", "Chabad", "Chaverim", "Chess Club", "Club Despertar", "College Democrats", "College Republicans", "CSC", "Cycling Club", "Daily Gazette", "Dance Forum", "Dare To Soar", "DESHI", "Drama Board", "Earthlust", "Enie", "ENLACE", "Feminist Majority", "FFS", "Folk Dance", "Free Culture", "Friends of Taiwan", "Global Health Forum", "Gospel Choir", "Grapevine", "Halcyon", "International Club", "Kitao Gallery", "Knit-Wits", "Learning For Life", "Mixed Company", "Mjumbe", "Mock Trial", "Motherpuckers", "Movie Committee", "MSA", "Multi", "Olde Club", "Outsiders", "Phoenix", "Photo Club", "Psi Phi", "Pun/ctum", "Quiz Bowl", "Rattech", "Rhythm N Motion", "Ruach", "SAC", "SAO", "SASA", "SASS", "SAVE R US", "SBA", "SBC", "SCCS", "SCF", "SCW", "SEA", "SHC", "SHIP", "Sixteen Feet", "SOCA", "Sound Machine", "SPC", "SPPC", "Spike Magazine", "SOFI", "SQU", "SSSL", "Student Council", "Swarthmore Good Food Project", "Swarthmore Massage", "Swarthmore Sudan", "Swat VOX", "Class Activists", "Van Coordinator", "Vertigo-go", "WRC", "WSRN")
for org in os:
    orgs.tags.create(name=org)

ds = ('Arabic', 'Art and Art History', 'Asian Studies', 'Astronomy', 'Biology', 'Black Studies', 'Chemistry and Biochemistry', 'Chinese', 'Classics', 'Cognitive Science', 'Comparative Literature', 'Computer Science', 'Dance', 'Economics', 'Educational Studies', 'Engineering',  'English Literature',  'Environmental Studies',  'Film and Media Studies',  'French',  'Gender and Sexuality Studies',  'German',  'German Studies',  'History',  'Interpretation Theory',  'Islamic Studies',  'Japanese',  'Latin American Studies',  'Linguistics',  'Mathematics and Statistics',  'Medieval Studies',  'Music',  'Peace and Conflict Studies',  'Philosophy',  'Physics',  'Political Science',  'Psychology',  'Public Policy',  'Religion',  'Russian',  'Sociology and Anthropology',  'Spanish',  'Theater')
for dept in ds:
    depts.tags.create(name=dept)

ps = ('Alice Paul', 'Amphitheater', 'Beardsley', 'Dana', 'David Kemp', 'Hallowell', 'Hicks', 'Kohlberg', 'Kyle', 'Lang Center', 'Lodges', 'LPAC', 'Mary Lyon', 'Mertz', 'Papazian', 'Parrish', 'Palmer', 'Pittenger', 'Roberts', 'SCCS Lounge', 'Science Center', 'Sharples', 'Strath Haven', 'Wharton', 'Willets', 'Woolman', 'Worth')
for place in ps:
    places.tags.create(name=place)

ppl = [('Al Bloom', 'President'), ('Jim Bock', 'Dean of Admissions'), ('Rachel Head', 'Housing Coordinator'), ('Jim Larimore', 'Dean of Students'), ('Martin Warner', 'Registrar'), ('Myrt Westphal', 'Dean of Student Life')]
for name, title in ppl:
    people.tags.create(name=name, long_name=("%s, %s" % (name, title)))


# ===================
# = Posts and Media =
# ===================

print "importing posts..."

posts = {}
media = {}


def download_file(url, target_dir):
    "Downloads the file at `url` to `target_dir` if it isn't there already."
    filename, ext = url.split('/')[-1].split('.', 1)
    import os.path
    target_path = os.path.join(target_dir, "%s.%s" % (filename, ext))
    
    if not os.path.exists(target_path):
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        import urllib2
        source = urllib2.urlopen(url)
        target = file(target_path, 'wb')
        print 'downloading %s...' % url, 
        # read in chunks, to avoid killing memory
        while True:
            read = source.read(128*1024)
            if not read:
                break
            target.write(read)
        print 'done.'
    return (filename, ext)

def resolve_media(url, article):
    """Takes a url and returns a media object for it."""
    if url not in media:
        slug = "old-" + article.slug
        bucket, created = MediaBucket.objects.get_or_create(slug=article.slug,
            defaults={'name': article.slug}
        )
        name, ext = download_file(url, "../gazjango/uploads/%s/" % bucket.slug)
        
        if re.match(r'jpe?g|png|gif', ext, re.IGNORECASE):
            klass = ImageFile
        else:
            klass = MediaFile
        
        media[url] = klass.objects.create(
            data="uploads/%s/%s.%s" % (bucket.slug, name, ext),
            slug=name[:50],
            pub_date=article.pub_date,
            bucket=bucket
        )
    return media[url]


query = "SELECT ID, post_author, post_date, post_title, post_content, post_excerpt, post_name " \
        "FROM gazette_posts WHERE post_type='post' AND post_status='publish';"
cursor.execute(query)
while True:
    row = cursor.fetchone()
    if row is None:
        break
    old_id, author, date, title, content, excerpt, slug = row
    author
    posts[int(old_id)] = defaultdict(lambda:"",
                                     author=author,
                                     date=date,
                                     title=title,
                                     content=content,
                                     excerpt=excerpt,
                                     slug=slug)

# find the ids of the terms we care about
taxonomy_ids = {}
relevant = ('news', 'features', 'arts', 'sports', 'opinion', 'multimedia') + \
           ('atg', 'weekend-roundup', 'editorials', 'stuco-platforms') + \
           ('announcements', 'gazette-news', 'jobs')
relevant = ', '.join("'%s'" % slug for slug in relevant)

cursor.execute("SELECT gazette_terms.slug, gazette_term_taxonomy.term_taxonomy_id " +
               "FROM gazette_terms, gazette_term_taxonomy " +
               "WHERE gazette_terms.term_id = gazette_term_taxonomy.term_id " +
               "AND gazette_terms.slug IN (%s) " % relevant +
               "ORDER BY gazette_term_taxonomy.taxonomy DESC")
# ordering is because there's both a post_tag and a category referring to
# the same term (#18) for athletics, and we want the category, not the tag
while True:
    row = cursor.fetchone()
    if not row:
        break
    slug, taxonomy_id = row
    taxonomy_ids[slug] = taxonomy_id

section_lookup = {
    taxonomy_ids['news']:       news,
    taxonomy_ids['features']:   features,
    taxonomy_ids['sports']:     athletics,
    taxonomy_ids['opinion']:    opinions_and_columns,
    taxonomy_ids['multimedia']: multimedia
}
subsection_lookup = {
    taxonomy_ids['atg']: atg,
    taxonomy_ids['weekend-roundup']: roundup,
    taxonomy_ids['stuco-platforms']: platforms
}
tag_lookup = {
    taxonomy_ids['arts']: arts
}
other_types_lookup = {
    taxonomy_ids['announcements']: 'announcement',
    taxonomy_ids['gazette-news']: 'gazette-news-announcement',
    taxonomy_ids['jobs']: 'jobs'
}

### not sure we necessarily want to tag based on autometa
# cursor.execute("SELECT post_id, meta_value FROM gazette_postmeta WHERE meta_key='autometa'")
# while True:
#     row = cursor.fetchone()
#     if row is None:
#         break
#     old_id, tags = row
#     try:
#         posts[int(old_id)]["tags"] = tags
#     except KeyError:
#         pass

# these are compiled to save a bit of speed, even though it kinda sucks
nextpage = re.compile(r'<!--\s*nextpage\s*-->')
empty    = re.compile(r'^\s*$')
part_matching = re.compile(r'''
    ^\s*                                    # start, whitespace
    <img[^>]+src=['"]([^'"]+)['"][^>]*/\s*> # img tag -- match only the src
    \s*                                     # probably some newlines
    (.*?)                                   # the caption: non-greedy match, to
                                            #           avoid ending whitespace
    \s*$                                    # whitespace, end of string
    ''', re.IGNORECASE | re.DOTALL | re.VERBOSE)

for post_id, p in posts.iteritems():
    section = subsection = None
    is_article = True
    is_announcement = is_gazette_news = is_job = False
    tags = []
    
    cursor.execute("SELECT term_taxonomy_id FROM gazette_term_relationships WHERE object_id = %s" % post_id)
    while True:
        row = cursor.fetchone()
        if not row:
            break
        taxo_id = row[0]
        if taxo_id in section_lookup:
            section = section_lookup[taxo_id]
        elif taxo_id in subsection_lookup:
            subsection = subsection_lookup[taxo_id]
        elif taxo_id in tag_lookup:
            tags.append(tag_lookup[taxo_id])
        elif taxo_id in other_types_lookup:
            is_article = False
            result = other_types_lookup[taxo_id]
            if result == "announcement":
                is_announcement = True
            elif result == "gazette-news-announcement":
                is_announcement = True
                is_gazette_news = True
            elif result == "jobs":
                is_job = True
            else:
                print "Unknown lookup result: %s" % result
    
    if is_article:
        content = p['content']

        if section is None:
            if subsection:
                section = subsection.section
            elif arts in tags:
                # assume that arts articles are features
                section = features
            elif ("Lunch" in content and "Dinner" in content) or post_id == 1121:
                continue # we're ignoring old menus for now
            elif "Today" in content and 'Tonight' in content and 'Tomorrow' in content:
                continue # TODO: parse the weather joke
            else:
                print "post %4s doesn't have a section" % post_id
                continue
        
        # TODO: process text
        
        summary = p['excerpt']
        if not summary:
            # wordpress just used the first 30 words, so we will too
            from django.utils.html import strip_tags
            summary = ' '.join(strip_tags(content).split()[:30])
        
        article_args = dict(
            headline=p['title'],
            slug=p['slug'][:50], # NOTE: slugs can't be > 50 chars on articles
            section=section,
            summary=summary,
            pub_date=p['date'],
            format=html,
            status='p',
        )
        
        if not nextpage.search(content):
            article = Article.objects.create(text=p['content'], **article_args)
        else: # this is probably a photospread
            article = PhotoSpread.objects.create(**article_args)
            
            parts = nextpage.split(content)
            for part in parts:
                if empty.match(part):
                    continue
                match = part_matching.match(part)
                if not match:
                    raise "Confused by photospread (id %s): %s" % (post_id, part)
                url, caption = match.groups()
                photo = resolve_media(url, article)
                article.add_photo(photo=photo, caption=caption)
        
        author_id = users[p['author']]['new_id']
        article.add_author(User.objects.get(pk=author_id).get_profile())    
    
        if subsection:
            article.subsections.add(subsection)
    
        if tags:
            article.tags = ','.join('"%s"' % tag.name for tag in tags)
    
        p["new_id"] = article.id
    elif is_announcement:
        if is_job:
            # NOTE: Jobs need some manual updating based on whether they're
            #       paid, on-campus, filled, etc....
            JobListing.objects.create(
                name=p['title'],
                slug=p['slug'][:50],
                description=p['content'],
                pub_date=p['date'],
                is_filled=True, # for most of them...
                is_published=True
            )
        else:
            d = p['date']
            date = datetime.date(d.year, d.month, d.day)
            Announcement.objects.create(
                kind=('s' if is_gazette_news else 'c'),
                title=p['title'],
                slug=p['slug'][:50],
                text=p['content'],
                date_start=date,
                date_end=date,
                is_published=True,
                sponsor='' # no real way to get this automatically
            )
    else:
        print 'unsure: skipping %s' % post_id

cursor.close()
conn.close()
