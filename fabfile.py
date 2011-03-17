from fabric.api import *

env.hosts = ['dailygazette@daily.swarthmore.edu']

def deploy():
    with cd('/home/dailygazette/gazjango-live'):
        run("git pull")
    run("touch /home/dailygazette/webapps/gazjango/gazjango.wsgi")
