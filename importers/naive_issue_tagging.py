#!/usr/bin/env python

import os.path
import sys

sys.path.extend([os.path.abspath(x) for x in (
    '..',
    '../gazjango',
    os.path.join(__file__, '..'),
    os.path.join(__file__, '../gazjango'),
)])

import settings
import django.core.management
django.core.management.setup_environ(settings)

import datetime
from gazjango.articles.models import Article
from gazjango.issues.models   import Issue, Weather, WeatherJoke, Menu

default_joke = WeatherJoke.objects.create(
    date=datetime.date(1864, 9, 1),
    line_one="This issue is from the time when we didn't save our weather jokes.",
    line_two="Utterly barbaric, I know.",
    line_three="But honestly? You're not missing much.",
)

default_menu = Menu.objects.create(
    date=datetime.date(1864, 9, 1),
    closed=True,
    message="Sharples was effectively closed this day, because we don't remember what they served.",
)

default_weather = Weather.objects.create(
    date=datetime.date(1864, 9, 1),
    today='',
    tomorrow='',
    tonight=''
)

zero = datetime.timedelta()
one_day = datetime.timedelta(days=1)

print 'adding articles to issues...',

for article in Article.objects.all():
    date = article.pub_date.date() + (one_day if article.pub_date.hour > 5 else zero)
    issue, created = Issue.objects.get_or_create(date=date,
        defaults={ 'menu': default_menu, 'weather': default_weather, 'joke': default_joke }
    )
    issue.articles.add(article)

print 'done.'
