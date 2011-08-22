#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This file spits out SQL suitable for importing all the articles and comments
from the old Django site into the new Wordpress site.
'''

URL = 'http://daily.swarthmore.edu'

import codecs
import datetime
import locale
import re
import sys

from collections import defaultdict, namedtuple
from django.utils.encoding import smart_unicode

# do Django setup
import settings
import django.core.management
django.core.management.setup_environ(settings)

# load all the models and so on
from interactive_load import *

# literal function to escape things going in SQL
User.objects.all()[0] # force a DB connection
_literal = django.db.connection.connection.literal

def literal(obj):
    if isinstance(obj, basestring):
        obj = smart_unicode(obj)
    return _literal(obj)

# wrap sys.stdout into a StreamWriter to allow writing unicode.
#sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout) 

# a silly little counter class
class Counter(object):
    def __init__(self, start=1):
        self.next = start
    def __call__(self):
        n = self.next
        self.next += 1
        return n

################################################################################

Table = namedtuple('Table', ['name', 'data', 'sql', 'fields'])

def do_tables(tables):
    for table in tables:
        print table.sql

    print 'LOCK TABLES %s;' % ', '.join('`%s` WRITE' % t.name for t in tables)

    for table in tables:
        print 'INSERT INTO `%s` (%s) VALUES' % (table.name,
                                                ', '.join(table.fields))
        print ',\n'.join('(%s)' % ', '.join(literal(x) for x in row)
                         for row in table.data)
        print ';'

    print 'UNLOCK TABLES;'

################################################################################
### Authors

wp_usermeta_info = {'sql': '''
--
-- Table structure for table `wp_usermeta`
--

DROP TABLE IF EXISTS `wp_usermeta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wp_usermeta` (
  `umeta_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) unsigned NOT NULL DEFAULT '0',
  `meta_key` varchar(255) DEFAULT NULL,
  `meta_value` longtext,
  PRIMARY KEY (`umeta_id`),
  KEY `user_id` (`user_id`),
  KEY `meta_key` (`meta_key`)
) ENGINE=MyISAM AUTO_INCREMENT=133 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
''',
    'fields': "umeta_id user_id meta_key meta_value".split()
}

wp_users_info = {'sql': '''
--
-- Table structure for table `wp_users`
--

DROP TABLE IF EXISTS `wp_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wp_users` (
  `ID` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `user_login` varchar(60) NOT NULL DEFAULT '',
  `user_pass` varchar(64) NOT NULL DEFAULT '',
  `user_nicename` varchar(50) NOT NULL DEFAULT '',
  `user_email` varchar(100) NOT NULL DEFAULT '',
  `user_url` varchar(100) NOT NULL DEFAULT '',
  `user_registered` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `user_activation_key` varchar(60) NOT NULL DEFAULT '',
  `user_status` int(11) NOT NULL DEFAULT '0',
  `display_name` varchar(250) NOT NULL DEFAULT '',
  PRIMARY KEY (`ID`),
  KEY `user_login_key` (`user_login`),
  KEY `user_nicename` (`user_nicename`)
) ENGINE=MyISAM AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
''',
        'fields':'ID user_login user_pass user_nicename user_email ' \
                  'user_registered display_name'.split()
}
AuthorInfo = namedtuple('AuthorInfo', wp_users_info['fields'])

def get_author_data():
    user_id_counter = Counter()
    umeta_counter = Counter()

    author_data = []
    author_meta = []

    author_pks = Writing.objects.all().values_list('user', flat=True).distinct()
    for author_pk in sorted(set(author_pks)):
        author = UserProfile.objects.get(pk=author_pk)
        author_id = user_id_counter()

        author_data.append(AuthorInfo(
                ID=author_id,
                user_login=author.username,
                user_pass='!',
                user_nicename=author.username,
                user_email=author.email,
                user_registered=author.user.date_joined,
                display_name=author.name,
        ))

        if author.editor_status():
            capabilities = 'a:1:{s:13:"administrator";s:1:"1";}'
            user_level = 10
        elif author.is_staff:
            capabilities = 'a:1:{s:11:"contributor";s:1:"1";}'
            user_level = 1
        else:
            capabilities = 'a:1:{s:10:"subscriber";s:1:"1";}'
            user_level = 0

        def meta(key, value):
            author_meta.append([umeta_counter(), author_id, key, value])

        meta('first_name', author.user.first_name)
        meta('last_name', author.user.last_name)
        meta('nickname', author.name)
        meta('description', '')
        meta('rich_editing', 'true')
        meta('comment_shortcuts', 'false')
        meta('admin_color', 'fresh')
        meta('use_ssl', '0')
        meta('show_admin_bar_front', 'true')
        meta('show_admin_bar_admin', 'false')
        meta('aim', '')
        meta('yim', '')
        meta('jabber', '')
        meta('wp_capabalities', capabilities)
        meta('wp_user_level', user_level)

    wp_users = Table('wp_users', data=author_data, **wp_users_info)
    wp_usermeta = Table('wp_usermeta', data=author_meta, **wp_usermeta_info)

    return wp_users, wp_usermeta

################################################################################
### Categories

wp_terms_info = {'sql': '''
--
-- Table structure for table `wp_terms`
--

DROP TABLE IF EXISTS `wp_terms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wp_terms` (
  `term_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL DEFAULT '',
  `slug` varchar(200) NOT NULL DEFAULT '',
  `term_group` bigint(10) NOT NULL DEFAULT '0',
  PRIMARY KEY (`term_id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=26 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
''',
    'fields': 'term_id name slug term_group'.split(),
}
WPTerm = namedtuple('WPTerm', wp_terms_info['fields'])

wp_term_taxonomy_info = {'sql': '''
--
-- Table structure for table `wp_term_taxonomy`
--

DROP TABLE IF EXISTS `wp_term_taxonomy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wp_term_taxonomy` (
  `term_taxonomy_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `term_id` bigint(20) unsigned NOT NULL DEFAULT '0',
  `taxonomy` varchar(32) NOT NULL DEFAULT '',
  `description` longtext NOT NULL,
  `parent` bigint(20) unsigned NOT NULL DEFAULT '0',
  `count` bigint(20) NOT NULL DEFAULT '0',
  PRIMARY KEY (`term_taxonomy_id`),
  UNIQUE KEY `term_id_taxonomy` (`term_id`,`taxonomy`),
  KEY `taxonomy` (`taxonomy`)
) ENGINE=MyISAM AUTO_INCREMENT=27 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
''',
    'fields': 'term_taxonomy_id term_id taxonomy description ' \
              'parent count'.split(),
}
WPTermTaxonomy = namedtuple('WPTermTaxonomy', wp_term_taxonomy_info['fields'])

# TODO - wp_term_relationships, also wp_term_taxonomy.count

def get_term_data():
    term_id_counter = Counter()
    term_taxonomy_counter = Counter()

    terms = []
    term_taxonomy = []
    term_ids = {}

    for section in Section.objects.all().order_by('slug'):
        term_ids[section] = term_id = term_id_counter()

        terms.append(WPTerm(
            term_id=term_id,
            name=section.name,
            slug=section.slug,
            term_group=0,
        ))

        term_taxonomy.append(WPTermTaxonomy(
            term_taxonomy_id=term_taxonomy_counter(),
            term_id=term_id,
            taxonomy='category',
            description=section.description,
            parent=0,
            count=0,
        ))

    for subsection in Subsection.objects.all().order_by('pk'):
        term_ids[subsection] = term_id = term_id_counter()

        terms.append(WPTerm(
            term_id=term_id,
            name=subsection.name,
            slug=subsection.slug,
            term_group=0,
        ))

        term_taxonomy.append(WPTermTaxonomy(
            term_taxonomy_id=term_taxonomy_counter(),
            term_id=term_id,
            taxonomy='category',
            description=subsection.description,
            parent=term_ids[subsection.section],
            count=0,
        ))

    terms = Table('wp_terms', data=terms, **wp_terms_info)
    tax = Table('wp_term_taxonomy', data=term_taxonomy, **wp_term_taxonomy_info)
    return terms, tax

################################################################################
### Posts

wp_post_info = {
    'fields': 'ID post_author post_date post_date_gmt post_content '\
              'post_title post_excerpt post_status comment_status ping_status '\
              'post_password post_name to_ping pinged post_modified '\
              'post_modified_gmt post_content_filtered post_parent guid '\
              'menu_order post_type post_mime_type comment_count'.split(),
    'sql': '''
--
-- Table structure for table `wp_posts`
--

DROP TABLE IF EXISTS `wp_posts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wp_posts` (
  `ID` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `post_author` bigint(20) unsigned NOT NULL DEFAULT '0',
  `post_date` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `post_date_gmt` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `post_content` longtext NOT NULL,
  `post_title` text NOT NULL,
  `post_excerpt` text NOT NULL,
  `post_status` varchar(20) NOT NULL DEFAULT 'publish',
  `comment_status` varchar(20) NOT NULL DEFAULT 'open',
  `ping_status` varchar(20) NOT NULL DEFAULT 'open',
  `post_password` varchar(20) NOT NULL DEFAULT '',
  `post_name` varchar(200) NOT NULL DEFAULT '',
  `to_ping` text NOT NULL,
  `pinged` text NOT NULL,
  `post_modified` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `post_modified_gmt` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `post_content_filtered` text NOT NULL,
  `post_parent` bigint(20) unsigned NOT NULL DEFAULT '0',
  `guid` varchar(255) NOT NULL DEFAULT '',
  `menu_order` int(11) NOT NULL DEFAULT '0',
  `post_type` varchar(20) NOT NULL DEFAULT 'post',
  `post_mime_type` varchar(100) NOT NULL DEFAULT '',
  `comment_count` bigint(20) NOT NULL DEFAULT '0',
  PRIMARY KEY (`ID`),
  KEY `post_name` (`post_name`),
  KEY `type_status_date` (`post_type`,`post_status`,`post_date`,`ID`),
  KEY `post_parent` (`post_parent`),
  KEY `post_author` (`post_author`)
) ENGINE=MyISAM AUTO_INCREMENT=321 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
'''
WPPost = namedtuple('WPPost', wp_post_info['fields']

wp_postmeta_info = {
    'fields': 'meta_id post_id meta_key meta_value'.split(),
    'sql': '''
--
-- Table structure for table `wp_postmeta`
--

DROP TABLE IF EXISTS `wp_postmeta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wp_postmeta` (
  `meta_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `post_id` bigint(20) unsigned NOT NULL DEFAULT '0',
  `meta_key` varchar(255) DEFAULT NULL,
  `meta_value` longtext,
  PRIMARY KEY (`meta_id`),
  KEY `post_id` (`post_id`),
  KEY `meta_key` (`meta_key`)
) ENGINE=MyISAM AUTO_INCREMENT=627 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
''',
}
WPPostMeta = namedtuple('WPPostMeta', wp_postmeta_info['fields']

wp_term_relationships_info = {
    'fields': 'object_id term_taxonomy_id term_order'.split(),
    'sql': '''
--
-- Table structure for table `wp_term_relationships`
--

DROP TABLE IF EXISTS `wp_term_relationships`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wp_term_relationships` (
  `object_id` bigint(20) unsigned NOT NULL DEFAULT '0',
  `term_taxonomy_id` bigint(20) unsigned NOT NULL DEFAULT '0',
  `term_order` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`object_id`,`term_taxonomy_id`),
  KEY `term_taxonomy_id` (`term_taxonomy_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
'''
}
WPTermRelationships = namedtuple('WPTermRelationships',
                                 wp_term_relationships_info['fields'])

_escape = re.compile(u'[\u0080-\uffff]+')
_entify = lambda c: '&#%d;' % ord(c)
def nicify(t):
    # TODO - are these replacements breaking HTML attributes?

    # FIXME - for now, just dropping unicode characters (including all quotation marks!)
    return _escape.sub("&apos;", smart_unicode(t).replace(u'\x10', ''))

    #return t.replace(u'\xc3\xad', "'") \
    #        .replace(u"\xe2\u20ac\u0153", u'\xe2\x80\x9c') \
    #        .replace(u"\xe2\u20ac\x9d", u'\xe2\x80\x9d') \
    #        .decode('utf-8', 'replace') \
    #        .replace(u'\u2019', "&#8217;") \
    #        .replace(u'\u201c', '&#8220;') \
    #        .replace(u'\u201d', '&#8221;') \
    #        .replace(u'\xed', "'") \
    #        .replace('\t', ' ')
    # \xed isn't actually an apostrophe, but it's in our DB like one


################################################################################

def main():
    do_tables(get_author_data())
    do_tables(get_term_data())

if __name__ == '__main__':
    main()

'''
# articles and comments
time_diff = datetime.timedelta(hours=-5)
for article in Article.published.all():
    a = etree.SubElement(channel, 'item')

    # titles, links, ids
    sub_text(a, 'title', article.headline)
    sub_text(a, WP+'post_name', article.slug)
    sub_text(a, 'link', URL + article.get_absolute_url())
    sub_text(a, 'guid', URL + article.get_absolute_url())
    sub_text(a, WP+'post_id', str(article.pk))

    # author
    sub_text(a, DC+'creator', article.authors_in_order()[0].username)
    # TODO - coauthors? http://wordpress.org/extend/plugins/co-authors-plus/

    # dates
    # NOTE: ignoring DST - fuck off
    sub_text(a, 'pubDate', nice_datify(article.pub_date))
    sub_text(a, WP+'post_date', datify(article.pub_date))
    sub_text(a, WP+'post_date_gmt', datify(article.pub_date + time_diff))

    # wordpress metadata that mostly doesn't change
    sub_text(a, WP+'comment_status', 'open' if article.comments_allowed else 'closed')
    sub_text(a, WP+'status', 'publish')
    sub_text(a, WP+'ping_status', 'open')
    sub_text(a, WP+'post_parent', '0')
    sub_text(a, WP+'menu_order', '0')
    sub_text(a, WP+'post_type', 'post')
    sub_text(a, WP+'post_password', '')
    sub_text(a, WP+'is_sticky', '0')

    # category
    s = article.sub_or_sec()
    sub_text(a, 'category', s.name, nicename=s.slug, domain='category')

    # content
    # TODO - deal with linked images, etc -- other changes to content
    try:
        n = nicify(article.resolved_text())
    except (UnicodeEncodeError, UnicodeDecodeError, ValueError):
        print >>sys.stderr, "Error with nicifying text of article %s" % article.pk

    try:
        sub_text(a, '{%s}encoded' % NS['content'], n)
    except (UnicodeEncodeError, UnicodeDecodeError, ValueError):
        print >>sys.stderr, "Error with content of article %s" % article.pk, s
                

    # TODO - does summary ever have textile?
    sub_text(a, '{%s}encoded' % NS['excerpt'], article.summary)

print etree.tostring(root, pretty_print=True)
'''
