from django.db import models
from django.contrib import admin
from gazjango.community.sources import utils
from gazjango.community.models import Entry
from django.template import Template
import datetime
import logging

log = logging.getLogger('community.sources.delicious')

# model definition
class Bookmark(Entry):
    class Meta:
        app_label = "community"
        ordering = ['-timestamp']

    @property
    def format_template(self):
        return Template("<div class='entry bookmark'><a href='{{ curr_object.url }}'>{{ curr_object.title }}</a></div>")


# admin definition
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'timestamp')
    date_hierarchy = 'timestamp'

# retrieve function
def retrieve(force, **args):
    if isinstance(args['account'], tuple) and len(args['account']) == 2:
        tag, password = args['account']
    else:
        tag = args['account']
        password = False
    url      = "http://feeds.delicious.com/v2/json/tag/%s" % tag
    rformat = 'json'

    last_update = datetime.datetime.fromtimestamp(0)
    if force:
        if password:
            url = "https://api.del.icio.us/v1/posts/all"
            rformat = "rss"
        log.info("Forcing update of all bookmarks available.")
    else:
        try:
            last_update = Bookmark.objects.filter(owner_user=tag+" - Tag").order_by('-timestamp')[0].timestamp
        except Exception, e:
            log.debug('%s', e)

    if force and password:
        marks = utils.get_remote_data(url, rformat=rformat, username=username, password=password)
    else:
        marks = utils.get_remote_data(url, rformat=rformat)

    if marks:
        for mark in marks:
            if password and force:
                _handle_rss_bookmark(mark, tag)
                continue
            dt = utils.parsedate(mark['dt']) 
            if dt > last_update:
                _handle_bookmark(mark, dt, tag)
            else:
                log.warning("No more bookmarks, stopping...")
                break

def _handle_bookmark(mark, dt, tag):
    log.info("working with bookmark => %s" % mark['d'])

    bookmark, created = Bookmark.objects.get_or_create(
        timestamp   = dt,
        url         = mark['u'],
        title       = mark['d'],
        owner_user  = tag+" - Tag",
        description = mark['n'],
        source_type = 'bookmark'
    )

def _handle_rss_bookmark(mark, username):
    log.info("working with bookmark => %s" % mark.get('extended'))

    bookmark, created = Bookmark.objects.get_or_create(
        description = mark.get('extended'),
        url = mark.get("href"),
        title = mark.get("description"),
        timestamp = utils.parsedate(mark.get('time'))
    )


admin.site.register(Bookmark, BookmarkAdmin)
