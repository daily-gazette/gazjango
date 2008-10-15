#!/usr/bin/env bash

cd $(dirname $0)
python=${1:-python}

echo "This will delete ALL DATA related to Django in your database."
echo "Are you absolutely sure this is what you want to do?"
echo -n 'Enter "yes" to continue: '
read resp
[[ "$resp" != "yes" ]] && exit

echo -n "clearing database..." && \
$python manage.py sqlclear \
$($python -c 'import settings; print " ".join(s.split(".")[-1] for s in settings.INSTALLED_APPS if s not in ("gazjango.misc", "django.contrib.admindocs", "django.contrib.humanize"))') \
| $python manage.py dbshell && \
echo "done." && \
echo -n "syncing database..." && \
$python manage.py syncdb --noinput --verbosity=0 && \
echo "done."
