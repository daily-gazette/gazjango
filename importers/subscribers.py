#!/usr/bin/env python

### set up django env
import os.path
import sys

sys.path.extend([os.path.abspath(x) for x in (
    '..',
    '../gazjango',
    # os.path.join(__file__, '..'),
    # os.path.join(__file__, '../gazjango'),
)])

import settings
import django.core.management
django.core.management.setup_environ(settings)

import re
import datetime
from gazjango.subscriptions.models import Subscriber
from gazjango.accounts.models      import UserProfile, UserKind

### connect to the old db
import MySQLdb as db
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-H", "--host",     dest="host",   help="connect to HOST",      metavar="HOST",   default="bruja.thewebhostingserver.com")
parser.add_option("-u", "--user",     dest="user",   help="authenticate as USER", metavar="USER",   default="gazette_plst1")
parser.add_option("-p", "--passwd",   dest="passwd", help="using PASSWD",         metavar="PASSWD", default="ZM2syVFzXwH4")
parser.add_option("-d", "--database", dest="db",     help="use database DB",      metavar="DB",     default="gazette_plst1")
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


### get the data

print "importing subscriptions..."
users = {}

# basics
cursor.execute("SELECT id, email, entered, modified, htmlemail, blacklisted FROM phplist_user_user WHERE confirmed = 1;")
while True:
    row = cursor.fetchone()
    if not row:
        break
    id, email, entered, modified, html, blacklisted = row
    users[id] = { 'email': email, 'html': html,
                  'subscribed': entered, 'modified': modified,
                  'blacklisted': blacklisted }

# names
cursor.execute("SELECT userid, value FROM phplist_user_user_attribute WHERE attributeid = 1;")
while True:
    row = cursor.fetchone()
    if not row:
        break
    id, val = row
    if id in users:
        users[id]['name'] = val

# types
cursor.execute("SELECT userid, value FROM phplist_user_user_attribute WHERE attributeid = 3;")
while True:
    row = cursor.fetchone()
    if not row:
        break
    id, val = row
    if id in users:
        users[id]['type'] = val

# history
cursor.execute("SELECT userid, date, summary, detail FROM phplist_user_user_history")
while True:
    row = cursor.fetchone()
    if not row:
        break
    userid, date, summary, detail = row
    if userid not in users:
        pass
    elif 'Confirmation' in summary or 'Subscription' in summary:
        users[userid]['subscribed'] = date
    elif 'Import' in summary:
        users[userid]['subscribed'] = users[userid].get('subscribed', None) or date
    elif 'Unsubscription' in summary:
        users[userid]['unsubscribed'] = date


# find out what the types mean, and make them into UserKinds
types = {}
unmatched_kinds = set()
student_re = re.compile(r'Student - (\d{4})')
cursor.execute("SELECT id, name FROM phplist_listattr_type1")
while True:
    row = cursor.fetchone()
    if not row:
        break
    id, name = row
    if name == 'Alum':
        kind, created = UserKind.objects.get_or_create(kind='a')
    elif name == 'Faculty/Staff':
        kind, created = UserKind.objects.get_or_create(kind='f')
    elif name == 'Parent':
        kind, created = UserKind.objects.get_or_create(kind='p')
    elif name == 'Prospective Student':
        kind, created = UserKind.objects.get_or_create(kind='k')
    elif name == 'Other':
        kind, created = UserKind.objects.get_or_create(kind='o')
    elif "Student" in name:
        year = student_re.match(name).group(1)
        kind, created = UserKind.objects.get_or_create(kind='s', year=year)
    else:
        unmatched_kinds.add(name)
        kind = None
    types[id] = kind


# make the subscriptions
for user_data in users.values():
    args = {}
    try:
        # there are 3 user profiles with mskorpe1
        user = UserProfile.objects.filter(user__email=user_data['email']).order_by('pk')[0]
        args['user'] = user
        if not user.kind or (user.kind.kind == 's' and user.kind.year is None):
            user.kind = types[int(user_data['type'])]
            user.save()
    except (UserProfile.DoesNotExist, IndexError):
        args['_email'] = user_data['email']
        args['_name'] = user_data.get('name', '')
        args['_kind'] = types[int(user_data['type'])]
    
    args['plain_text'] = not user_data['html']
    args['is_confirmed'] = True
    try:
        subscriber = Subscriber.objects.create(**args)
    except:
        print args
        raise
    
    subscriber.subscribed = user_data['subscribed']
    if 'unsubscribed' in user_data:
        subscriber.unsubscribed = user_data['unsubscribed']
    elif user_data['blacklisted']:
        subscriber.unsubscribed = datetime.datetime.now()
    subscriber.save()
