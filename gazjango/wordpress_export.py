#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This file spits out SQL suitable for importing all the articles and comments
from the old Django site into the new Wordpress site.
'''

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

URL = 'http://daily.swarthmore.edu'
TIME_DIFF = datetime.timedelta(hours=-5) # ignoring DST - fuck off

################################################################################

Table = namedtuple('Table', ['name', 'data', 'sql', 'fields'])

def do_tables(tables):
    for table in tables:
        print table.sql

    print 'LOCK TABLES %s;' % ', '.join('`%s` WRITE' % t.name for t in tables)

    for table in tables:
        if table.data:
            print 'INSERT INTO `%s` (%s) VALUES' % (table.name,
                                                    ', '.join(table.fields))
            print ',\n'.join('(%s)' % ', '.join(literal(x) for x in row)
                             for row in table.data)
            print ';'

    print 'UNLOCK TABLES;'

################################################################################
### Authors

# TODO - why can't you log into the admin?

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

def get_authors():
    user_id_counter = Counter()
    umeta_counter = Counter()

    author_data = []
    author_meta = []

    author_ids = {}

    author_pks = Writing.objects.all().values_list('user', flat=True).distinct()
    for author_pk in sorted(set(author_pks)):
        author = UserProfile.objects.get(pk=author_pk)
        author_ids[author] = author_id = user_id_counter()

        author_data.append(AuthorInfo(
                ID=author_id,
                user_login=author.username,
                user_pass='!',
                user_nicename=author.username,
                user_email=author.email,
                user_registered=author.user.date_joined,
                display_name=author.name,
        ))

        if author.user.is_superuser or author.editor_status():
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

    return (wp_users, wp_usermeta), author_ids

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

def get_terms(author_ids):
    terms = []
    term_taxonomy = []

    term_id_counter = Counter()
    term_taxonomy_counter = Counter()
    term_ids = {}
    taxonomy_ids = {}

    for section in Section.objects.all().order_by('slug'):
        term_ids[section] = term_id = term_id_counter()
        taxonomy_ids[section] = taxonomy_id = term_taxonomy_counter()

        terms.append(WPTerm(
            term_id=term_id,
            name=section.name,
            slug=section.slug,
            term_group=0,
        ))

        term_taxonomy.append(WPTermTaxonomy(
            term_taxonomy_id=taxonomy_id,
            term_id=term_id,
            taxonomy='category',
            description=section.description,
            parent=0,
            count=0,
        ))

    for subsection in Subsection.objects.all().order_by('pk'):
        term_ids[subsection] = term_id = term_id_counter()
        taxonomy_ids[subsection] = taxonomy_id = term_taxonomy_counter()

        terms.append(WPTerm(
            term_id=term_id,
            name=subsection.name,
            slug=subsection.slug,
            term_group=0,
        ))

        term_taxonomy.append(WPTermTaxonomy(
            term_taxonomy_id=taxonomy_id,
            term_id=term_id,
            taxonomy='category',
            description=subsection.description,
            parent=term_ids[subsection.section],
            count=0, 
        ))

    # make entries for co-authors+
    for author, aid in author_ids.iteritems():
        term_ids[author] = term_id = term_id_counter()
        taxonomy_ids[author] = taxonomy_id = term_taxonomy_counter()

        terms.append(WPTerm(
            term_id=term_id,
            name=author.username,
            slug=author.username,
            term_group=0,
        ))

        term_taxonomy.append(WPTermTaxonomy(
            term_taxonomy_id=taxonomy_id,
            term_id=term_id,
            taxonomy='author',
            description='',
            parent=0,
            count=0,
        ))


    terms = Table('wp_terms', data=terms, **wp_terms_info)
    tax = Table('wp_term_taxonomy', data=term_taxonomy, **wp_term_taxonomy_info)
    return (terms, tax), term_ids, taxonomy_ids

################################################################################
### Posts

wp_posts_info = {
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
}
WPPost = namedtuple('WPPost', wp_posts_info['fields'])

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
WPPostMeta = namedtuple('WPPostMeta', wp_postmeta_info['fields'])

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

#_escape = re.compile(u'[\u0080-\uffff]+')
#_entify = lambda c: '&#%d;' % ord(c)
def nicify_content(t):
    # TODO - deal with smart quotes, other unicode
    # TODO - change <div>s for images to make sense on new site
    return smart_unicode(t).replace(u'\x10', '')

    #return _escape.sub("&apos;", smart_unicode(t).replace(u'\x10', ''))

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

def get_posts(author_ids, taxonomy_ids):
    posts = []
    postmeta = []
    term_relns = []

    article_ids = {}
    article_id_counter = Counter()

    # do the base article stuff
    for article in Article.published.all():
        article_ids[article] = article_id = article_id_counter()

        authors = article.authors_in_order()

        # do the basic post
        posts.append(WPPost(
            ID=article_id,
            post_author=author_ids[authors[0]],

            post_title=article.headline,
            post_name=article.slug,
            guid=URL + article.get_absolute_url(),

            post_excerpt=article.summary,

            post_date=article.pub_date,
            post_date_gmt=article.pub_date+TIME_DIFF,
            post_modified=article.pub_date,
            post_modified_gmt=article.pub_date+TIME_DIFF,

            post_content=nicify_content(article.resolved_text()),
            post_content_filtered='',

            post_status='publish',
            comment_status=article.comments_allowed,
            ping_status='open',
            to_ping='',
            pinged='',
            
            post_password='',
            post_parent=0,
            menu_order=0,
            post_type='post',
            post_mime_type='',
            comment_count=0, # will be updated laterz
        ))

        term_counter = Counter()
        def add_term(taxonomy_id):
            term_relns.append(WPTermRelationships(
                object_id=article_id,
                term_taxonomy_id=taxonomy_id,
                term_order=term_counter(),
            ))


        # connect to sections
        add_term(taxonomy_ids[article.section])
        if article.subsection:
            add_term(taxonomy_ids[article.subsection])

        # connect to author terms
        for author in authors:
            add_term(taxonomy_ids[author])

    # TODO - do "attachment" posts (ie images)
    # TODO - handle photospreads

    # TODO - do postmeta stuff...what matters?
    #  _thumbnail_id, _wp_attached_file, _wp_attachment_metadata, _oembed_ crap

    wp_posts = Table('wp_posts', data=posts, **wp_posts_info)
    wp_postmeta = Table('wp_postmeta', data=postmeta, **wp_postmeta_info)
    wp_term_relns = Table('wp_term_relationships', data=term_relns,
                          **wp_term_relationships_info)

    return (wp_posts, wp_postmeta, wp_term_relns), article_ids


################################################################################
### Comments

wp_comments_info = {
    'fields': 'comment_ID comment_post_ID comment_author comment_author_email '\
              'comment_author_url comment_author_IP comment_date ' \
              'comment_date_gmt comment_content comment_karma comment_approved '\
              'comment_agent comment_type comment_parent user_id'.split(),
    'sql': '''
--
-- Table structure for table `wp_comments`
--

DROP TABLE IF EXISTS `wp_comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wp_comments` (
  `comment_ID` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `comment_post_ID` bigint(20) unsigned NOT NULL DEFAULT '0',
  `comment_author` tinytext NOT NULL,
  `comment_author_email` varchar(100) NOT NULL DEFAULT '',
  `comment_author_url` varchar(200) NOT NULL DEFAULT '',
  `comment_author_IP` varchar(100) NOT NULL DEFAULT '',
  `comment_date` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `comment_date_gmt` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `comment_content` text NOT NULL,
  `comment_karma` int(11) NOT NULL DEFAULT '0',
  `comment_approved` varchar(20) NOT NULL DEFAULT '1',
  `comment_agent` varchar(255) NOT NULL DEFAULT '',
  `comment_type` varchar(20) NOT NULL DEFAULT '',
  `comment_parent` bigint(20) unsigned NOT NULL DEFAULT '0',
  `user_id` bigint(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`comment_ID`),
  KEY `comment_approved` (`comment_approved`),
  KEY `comment_post_ID` (`comment_post_ID`),
  KEY `comment_approved_date_gmt` (`comment_approved`,`comment_date_gmt`),
  KEY `comment_date_gmt` (`comment_date_gmt`),
  KEY `comment_parent` (`comment_parent`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
''',
}
WPComment = namedtuple('WPComment', wp_comments_info['fields'])

wp_commentmeta_info = {
    'fields': 'meta_id comment_id meta_key meta_value'.split(),
    'sql': '''
--
-- Table structure for table `wp_commentmeta`
--

DROP TABLE IF EXISTS `wp_commentmeta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wp_commentmeta` (
  `meta_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `comment_id` bigint(20) unsigned NOT NULL DEFAULT '0',
  `meta_key` varchar(255) DEFAULT NULL,
  `meta_value` longtext,
  PRIMARY KEY (`meta_id`),
  KEY `comment_id` (`comment_id`),
  KEY `meta_key` (`meta_key`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
'''
}
WPCommentMeta = namedtuple('WPCommentMeta', wp_commentmeta_info['fields'])    

def get_comments(author_ids, article_ids):
    comments = []
    commentmeta = []

    comment_ids = {}
    comment_id_counter = Counter()
    comment_meta_counter = Counter()

    for comment in PublicComment.objects.all().select_related(depth=1):
        comment_id = comment_ids[comment] = comment_id_counter()
        article_id = article_ids[comment.subject]

        user_id = 0
        email = comment.email
        if comment.user:
            email = comment.user.email
            if comment.user in author_ids:
                user_id = author_ids[comment.user]

        comments.append(WPComment(
            comment_ID=comment_id,
            comment_post_ID=article_id,
            comment_author=comment.display_name,
            comment_author_email=email,
            comment_author_url='',
            comment_author_IP=comment.ip_address,
            comment_date=comment.time,
            comment_date_gmt=comment.time+TIME_DIFF,
            comment_content=comment.text,
            comment_karma=comment.score,
            comment_approved=comment.is_visible(),
            comment_agent=comment.user_agent,
            comment_type='',
            comment_parent='0',
            user_id=user_id,
        ))

    wp_comments = Table('wp_comments', data=comments, **wp_comments_info)
    wp_cmeta = Table('wp_commentmeta', data=commentmeta, **wp_commentmeta_info)

    return (wp_comments, wp_cmeta), comment_ids
        

################################################################################

def main():
    tables, author_ids = get_authors()
    do_tables(tables)

    tables, term_ids, taxonomy_ids = get_terms(author_ids)
    do_tables(tables)

    tables, article_ids = get_posts(author_ids, taxonomy_ids)
    do_tables(tables)

    tables, comment_ids = get_comments(author_ids, article_ids)
    do_tables(tables)

    # update wp_term_taxonomy.count
    print "LOCK TABLES `wp_term_taxonomy` WRITE, `wp_term_relationships` WRITE;"
    print "UPDATE `wp_term_taxonomy` SET count=(SELECT COUNT(*) FROM `wp_term_relationships` WHERE `wp_term_relationships`.`term_taxonomy_id` = `wp_term_taxonomy`.`term_taxonomy_id`);"
    print "UNLOCK TABLES;"

    # update wp_posts.comment_count
    print "LOCK TABLES `wp_posts` WRITE, `wp_comments` WRITE;"
    print "UPDATE `wp_posts` SET comment_count=(SELECT COUNT(*) FROM `wp_comments` WHERE `wp_comments`.`comment_post_ID` = `wp_posts`.`ID`);"
    print "UNLOCK TABLES;"

if __name__ == '__main__':
    main()
