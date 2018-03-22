import random
import os
from fabric.contrib.files import append, exists
from fabric.api import cd, env, local, run

REPO_URL = 'https://github.com/dominicwhite/django-tdd.git'

def deploy():
    site_folder = '/home/'+env.user+'/sites/'+env.host
    run('mkdir -p '+site_folder)
    with cd(site_folder):
        _get_latest_source()
        _update_virtualenv()
        _create_or_update_dotenv()
        _update_static_files()
        _update_database()

def _get_latest_source():
    if exists('.git'):
        run('git fetch')
    else:
        run('git clone '+REPO_URL+' .')
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run('git reset --hard '+current_commit)

def _update_virtualenv():
    if not exists('virtualenv/bin/pip'):
        run('python3 -m venv virtualenv')
    run('./virtualenv/bin/pip install -r requirements.txt')

def _create_or_update_dotenv():
    append('.env', 'DJANGO_DEBUG_FALSE=y')
    append('.env', 'SITENAME='+env.host)
    current_contents = run('cat .env')
    if 'DJANGO_SECRET_KEY' not in current_contents:
        new_secret = ''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789') for i in range(50)])
        append('.env', 'DJANGO_SECRET_KEY='+new_secret)

def _update_static_files():
    with cd('superlists_project'):
        run('../virtualenv/bin/python manage.py collectstatic --noinput')

def _update_database():
    with cd('superlists_project'):
        run('../virtualenv/bin/python manage.py migrate --noinput')
