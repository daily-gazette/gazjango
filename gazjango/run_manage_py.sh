appdir=/home/dailygazette/webapps/gazjango
appname=gazjango

export PATH=$HOME/bin:$PATH
export PYTHONPATH=$appdir/lib/python2.6:$appdir:
export DJANGO_SETTINGS_MODULE=$appname.settings

python $appdir/$appname/manage.py $*
