import os
import sys
import django.core.handlers.wsgi

PROJNAME = 'phoenix'
PROJPATH = '/var/www/phoenix/'

# Add Project Path to sys.path
sys.path.append(PROJPATH)
sys.path.append('%s/%s' %(PROJPATH,PROJNAME))

# Add Project Settings to os.environment
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

# Implement Django's WSGI Handler
application = django.core.handlers.wsgi.WSGIHandler()
