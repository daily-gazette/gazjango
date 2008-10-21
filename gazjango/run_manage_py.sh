appdir=/home/dailygazette/webapps/django_trunk
appname=gazjango

export PATH=$HOME/bin:$PATH
export PYTHONPATH=$appdir/lib/python2.5:$appdir:
export DJANGO_SETTINGS_MODULE=$appname.settings

python $appdir/$appname/manage.py $*
