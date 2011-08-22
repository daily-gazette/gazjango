#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This file creates a Wordpress eXtended RSS (WXR) file with all of the articles
and comments from the Django site, for importing into the new Wordpress site.
'''

import settings
import django.core.management
django.core.management.setup_environ(settings)

from interactive_load import *

from django.utils.encoding import smart_unicode
from collections import defaultdict
import datetime
from lxml import etree
import re
import sys

URL = 'http://daily.swarthmore.edu'

class Counter(object):
    def __init__(self, start=1):
        self.next = start
    def __call__(self):
        n = self.next
        self.next += 1
        return n

def sub_text(parent, tag, text=None, **extra):
    el = etree.SubElement(parent, tag, **extra)
    el.text = text
    return el

def nice_datify(d):
    # hack to avoid doing real timezones
    return d.strftime('%a, %d %b %Y %H:%M:%S -0500')

def datify(d):
    return d.strftime('%Y-%m-%d %H:%M:%S')


_escape = re.compile(u'[\u0080-\uffff]+')
_entify = lambda c: '&#%d;' % ord(c)
def nicify(t):
    # inefficient but lazy
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


NS = dict(excerpt="http://wordpress.org/export/1.1/excerpt/",
          content="http://purl.org/rss/1.0/modules/content/",
          wfw="http://wellformedweb.org/CommentAPI/",
          dc="http://purl.org/dc/elements/1.1/",
          wp="http://wordpress.org/export/1.1/")
WP = '{%s}' % NS['wp']
DC = '{%s}' % NS['dc']

root = etree.Element('rss', nsmap=NS)

channel = etree.SubElement(root, 'channel')
c = lambda *a, **k: sub_text(channel, *a, **k)

# basic metadata
c('title', "Daily Gazette")
c('link', URL)
c('description', "Swarthmore's Daily Paper")
c('pubDate', nice_datify(datetime.datetime.now()))
c('language', 'en')
c(WP+'wxr_version' % NS, '1.1')
c(WP+'base_site_url' % NS, URL)
c(WP+'base_blog_url' % NS, URL)

# authors
author_ids = defaultdict(Counter())

author_pks = Writing.objects.all().values_list('user', flat=True).distinct()
for author_pk in sorted(set(author_pks)):
    author = UserProfile.objects.get(pk=author_pk)

    a = etree.SubElement(channel, WP+'author')
    sub_text(a, WP+'author_id', str(author_ids[author]))
    sub_text(a, WP+'author_login', author.username)
    sub_text(a, WP+'author_email', author.email)
    sub_text(a, WP+'author_display_name', author.name)
    sub_text(a, WP+'author_first_name', author.user.first_name)
    sub_text(a, WP+'author_last_name', author.user.last_name)

# categories
section_ids = defaultdict(Counter())

for section in Section.objects.all().order_by('pk'):
    s = etree.SubElement(channel, WP+'category')
    sub_text(s, WP+'term_id', str(section_ids[section]))
    # apparently nicename=slug, name=human-readable. seems backwards...
    sub_text(s, WP+'category_nicename', section.slug)
    sub_text(s, WP+'cat_name', section.name)
    sub_text(s, WP+'category_description', section.description)
    sub_text(s, WP+'category_parent', '')

for subsection in Subsection.objects.all().order_by('pk'):
    s = etree.SubElement(channel, WP+'category')
    sub_text(s, WP+'term_id', str(section_ids[subsection]))
    # apparently nicename=slug, name=human-readable. seems backwards...
    sub_text(s, WP+'category_nicename', subsection.slug)
    sub_text(s, WP+'cat_name', subsection.name)
    sub_text(s, WP+'category_description', subsection.description)
    sub_text(s, WP+'category_parent', subsection.section.slug)

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
