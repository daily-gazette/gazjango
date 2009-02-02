#!/usr/bin/env python

from optparse import OptionParser
import re

# =======================
# = database connection =
# =======================
import MySQLdb as db

parser = OptionParser()
parser.add_option("-H", "--host",     dest="host",   help="connect to HOST",      metavar="HOST",   default="localhost")
parser.add_option("-u", "--user",     dest="user",   help="authenticate as USER", metavar="USER",   default="root")
parser.add_option("-p", "--passwd",   dest="passwd", help="using PASSWD",         metavar="PASSWD", default="")
parser.add_option("-d", "--database", dest="db",     help="use database DB",      metavar="DB",     default="gazette")
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


# =================
# = load old data =
# =================

print "loading old data..."

# all of our mediafiles are actually imagefiles anyway
cursor.execute("SELECT mediafile_ptr_id FROM media_imagefile;")
image_ids = set(row[0] for row in cursor.fetchall())

def iterfetch(cursor):
    while True:
        row = cursor.fetchone()
        if not row:
            break
        yield row

media_fields = "id data name slug bucket_id description author_name pub_date source_url license_type".split()
cursor.execute("SELECT %s FROM media_mediafile;" % ', '.join(media_fields))
old_mediafiles = dict( (row[0], dict(zip(media_fields, row))) for row in iterfetch(cursor) )

cursor.execute("SELECT mediafile_id, userprofile_id FROM media_mediafile_users")
for mediafile_id, userprofile_id in iterfetch(cursor):
    if 'users' not in old_mediafiles[mediafile_id]:
        old_mediafiles[mediafile_id]['users'] = set()
    old_mediafiles[mediafile_id]['users'].add(userprofile_id)

article_fields = "id front_image_id issue_image_id thumbnail_id".split()
cursor.execute("SELECT %s FROM articles_article;" % ', '.join(article_fields))
articles = dict( (row[0], dict(zip(article_fields, row))) for row in iterfetch(cursor) )

# ======================================
# = figure out how to process the data =
# ======================================

print "figuring out what data we need to make"
new_imagefiles = {}
class Counter(object):
    def __init__(self, num=0):
        self.num = num
    
    def next(self):
        self.num += 1
        return self.num
    
imagefiles_counter = Counter()

# name_suffix = re.compile(
#     r'\s*(\s*[\(_-]?(front|issue|thumb|top|mid|tall|square|wide)[\)_-]?){1,}\s*$',
#     re.IGNORECASE
# )

def add_new_imagefile(data):
    key = (data['bucket_id'], data['slug'])
    if key in new_imagefiles:
        print 'merging for %s/%s' % key
        existing = new_imagefiles[key]
        for field in data:
            existing[field] = existing.get(field, None) or data[field]
    else:
        new_imagefiles[key] = data
        new_imagefiles[key]['new_id'] = imagefiles_counter.next()
    return new_imagefiles[key]

for article in articles.values():
    images = {}
    if article['thumbnail_id']:
        images['thumb'] = old_mediafiles[article['thumbnail_id']]
    if article['front_image_id']:
        images['front'] = old_mediafiles[article['front_image_id']]
    if article['issue_image_id']:
        images['issue'] = old_mediafiles[article['issue_image_id']]
        
    if images:
        data = {}
        for kind, image in images.items():
            for field in image:
                data[field] = data.get(field, None) or image[field]
            data['_%s_data' % kind] = image['data']
            image['processed'] = True
        
        data['old_ids'] = set(image['id'] for image in images.values())
        data['old_slugs'] = set((image['bucket_id'], image['slug'])
                                for image in images.values()
                                if image['slug'] != data['slug'])
        # TODO: fix broken links to these images
        
        # data['name'] = name_suffix.sub('', data['name'])
        # data['slug'] = name_suffix.sub('', data['slug'])
        new = add_new_imagefile(data)
        article['main_image_id'] = new['new_id']
        for image in images.values():
            image['new_id'] = new['new_id']

for image in old_mediafiles.values():
    if image.get('processed', False):
        continue
    add_new_imagefile(image)


# =====================
# = create new tables =
# =====================

print "killing old media_imagefile table"
cursor.execute("DROP TABLE `media_imagefile`")
cursor.execute("DELETE FROM articles_article_media;") # these are just caches anyway

print "making new media_imagefile table, etc"
cursor.execute("""CREATE TABLE `media_imagefile` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(100) NOT NULL,
    `slug` varchar(50) NOT NULL,
    `bucket_id` integer NOT NULL,
    `author_name` varchar(100) NOT NULL,
    `license_type` varchar(1) NOT NULL,
    `source_url` varchar(200) NOT NULL,
    `description` longtext NOT NULL,
    `pub_date` datetime NOT NULL,
    `data` varchar(100) NOT NULL,
    `front_is_tall` bool NOT NULL,
    `_front_data` varchar(100) NOT NULL,
    `_issue_data` varchar(100) NOT NULL,
    `_thumb_data` varchar(100) NOT NULL,
    UNIQUE (`slug`, `bucket_id`)
);""")
cursor.execute('ALTER TABLE `media_imagefile` ADD CONSTRAINT `bucket_id_refs_id_37bbd69a` FOREIGN KEY (`bucket_id`) REFERENCES `media_mediabucket` (`id`);')

cursor.execute("""CREATE TABLE `media_imagefile_users` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `imagefile_id` integer NOT NULL,
    `userprofile_id` integer NOT NULL,
    UNIQUE (`imagefile_id`, `userprofile_id`)
);""")
cursor.execute('ALTER TABLE `media_imagefile_users` ADD CONSTRAINT `imagefile_id_refs_id_13b4f2` FOREIGN KEY (`imagefile_id`) REFERENCES `media_imagefile` (`id`);')
cursor.execute('ALTER TABLE `media_imagefile_users` ADD CONSTRAINT `userprofile_id_refs_id_43f44e60` FOREIGN KEY (`userprofile_id`) REFERENCES `accounts_userprofile` (`id`);')

# cursor.execute('CREATE INDEX `media_mediafile_slug` ON `media_mediafile` (`slug`);')
# cursor.execute('CREATE INDEX `media_mediafile_bucket_id` ON `media_mediafile` (`bucket_id`);')
cursor.execute('CREATE INDEX `media_imagefile_slug` ON `media_imagefile` (`slug`);')
cursor.execute('CREATE INDEX `media_imagefile_bucket_id` ON `media_imagefile` (`bucket_id`);')

cursor.execute('ALTER TABLE `articles_article` ADD COLUMN `main_image_id` integer;')
cursor.execute('ALTER TABLE `articles_article` ADD CONSTRAINT `main_image_id_refs_id_41d05108` FOREIGN KEY (`main_image_id`) REFERENCES `media_imagefile` (`id`);')
cursor.execute('CREATE INDEX `articles_article_main_image_id` ON `articles_article` (`main_image_id`);')

cursor.execute('ALTER TABLE `articles_article_media` ADD CONSTRAINT `article_id_refs_id_17f7e198` FOREIGN KEY (`article_id`) REFERENCES `articles_article` (`id`);')
cursor.execute('ALTER TABLE `articles_article_media` ADD CONSTRAINT `mediafile_id_refs_id_54041a1a` FOREIGN KEY (`mediafile_id`) REFERENCES `media_mediafile` (`id`);')
cursor.execute('''CREATE TABLE `articles_article_images` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `article_id` integer NOT NULL,
    `imagefile_id` integer NOT NULL,
    UNIQUE (`article_id`, `imagefile_id`)
);''')
cursor.execute('ALTER TABLE `articles_article_images` ADD CONSTRAINT `article_id_refs_id_5c49b9b9` FOREIGN KEY (`article_id`) REFERENCES `articles_article` (`id`);')
cursor.execute('ALTER TABLE `articles_article_images` ADD CONSTRAINT `imagefile_id_refs_id_509588a` FOREIGN KEY (`imagefile_id`) REFERENCES `media_imagefile` (`id`);')


# ========================
# = make the actual data =
# ========================

print "making new images..."

slug_changes = {}

for image in new_imagefiles.values():
    cursor.execute("""INSERT INTO media_imagefile SET
        `id`=%s,
        `name`=%s,
        `slug`=%s,
        `bucket_id`=%s,
        `author_name`=%s,
        `license_type`=%s,
        `source_url`=%s,
        `description`=%s,
        `pub_date`=%s,
        `data`=%s,
        `front_is_tall`=%s,
        `_front_data`=%s,
        `_issue_data`=%s,
        `_thumb_data`=%s;
    """,
    (   image['new_id'],
        image['name'],
        image['slug'],
        image['bucket_id'],
        image['author_name'],
        image['license_type'],
        image['source_url'],
        image['description'],
        image['pub_date'].strftime("%Y-%m-%d %H-%M-%S"),
        image['data'],
        0,
        image.get('_front_data', ''),
        image.get('_issue_data', ''),
        image.get('_thumb_data', '')
    ))
    
    if 'old_slugs' in image:
        for old_bucket, old_slug in image['old_slugs']:
            slug_changes[(old_bucket, old_slug)] = (image['bucket_id'], image['slug'])
    
    if 'users' in image:
        for user_id in image['users']:
            cursor.execute("INSERT INTO media_imagefile_users "
                           "SET imagefile_id=%s, userprofile_id=%s" %
                           (image['new_id'], user_id))

print "\nSLUG CORRESPONDENCES:\n"
for (old_bucket, old_slug), (new_bucket, new_slug) in slug_changes.items():
    print "%s/%s => %s/%s" % (old_bucket, old_slug, new_bucket, new_slug)
print "\n\n"
print "updating articles..."
for article in articles.values():
    if 'main_image_id' in article:
        cursor.execute("UPDATE articles_article SET main_image_id=%s WHERE id=%s",
                       (article['main_image_id'], article['id']))


def get_new_image_id(old_image_id):
    old = old_mediafiles[old_image_id]
    old_bucket = old['bucket_id']
    old_slug = old['slug']
    new_bucket, new_slug = slug_changes.get((old_bucket, old_slug), (old_bucket, old_slug))
    return new_imagefiles[(new_bucket, new_slug)]['new_id']

print "updating specials..."
cursor.execute("SELECT id, image_id FROM articles_special")
for id, image_id in cursor.fetchall():
    cursor.execute("UPDATE articles_special SET image_id=%s WHERE id=%s",
                   (get_new_image_id(image_id), id))

print "updating photospreads..."
cursor.execute("SELECT id, photo_id FROM articles_photoinspread")
for id, photo_id in cursor.fetchall():
    cursor.execute("UPDATE articles_photoinspread SET photo_id=%s WHERE id=%s",
                   (get_new_image_id(photo_id), id))

print "updating athletics..."
cursor.execute("SELECT id, icon_id FROM athletics_team")
for id, icon_id in cursor.fetchall():
    cursor.execute("UPDATE athletics_team SET icon_id=%s WHERE id=%s",
                   (get_new_image_id(icon_id), id))

print "updating profiles..."
cursor.execute("SELECT id, picture_id FROM accounts_userprofile WHERE picture_id")
for id, picture_id in cursor.fetchall():
    print (get_new_image_id(picture_id), id)
    cursor.execute("UPDATE accounts_userprofile SET picture_id=%s WHERE id=%s",
                   (get_new_image_id(picture_id), id))

# i checked, and this shouldn't break any article-internal links

# =========================================
# = delete old imagefiles, unused columns =
# =========================================

print "deleting old data"
cursor.execute("DELETE FROM media_mediafile WHERE id NOT IN (%s)" %
               ', '.join(str(id) for id in image_ids))
cursor.execute("ALTER TABLE articles_article DROP COLUMN front_image_id")
cursor.execute("ALTER TABLE articles_article DROP COLUMN issue_image_id")
cursor.execute("ALTER TABLE articles_article DROP COLUMN thumbnail_id")
