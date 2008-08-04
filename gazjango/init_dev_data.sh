#!/usr/bin/env bash

echo "This will delete ALL DATA related to Django in your database."
echo "Are you absolutely sure this is what you want to do?"
echo -n 'Enter "yes" to continue: '
read resp
[[ "$resp" != "yes" ]] && exit

./manage.py reset --noinput `python -c 'import settings; print " ".join(s.split(".")[-1] for s in settings.INSTALLED_APPS if not s.endswith("misc"))'` && echo "done resetting" && ./manage.py syncdb && echo "done syncing" && ./init_dev_data.py && echo "done initting"
