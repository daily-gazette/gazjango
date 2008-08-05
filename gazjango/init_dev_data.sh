#!/usr/bin/env bash

python=${1:-python}

echo "This will delete ALL DATA related to Django in your database."
echo "Are you absolutely sure this is what you want to do?"
echo -n 'Enter "yes" to continue: '
read resp
[[ "$resp" != "yes" ]] && exit

$python manage.py sqlclear \
$($python -c 'import settings; print " ".join(s.split(".")[-1] for s in settings.INSTALLED_APPS if not s.endswith("misc"))') \
| $python manage.py dbshell && \
echo "database cleared" && \
$python manage.py syncdb --noinput --verbosity=0 && \
echo "database synced" && \
$python init_dev_data.py && \
echo "data init'ed"
