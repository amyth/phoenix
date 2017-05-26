#!/usr/bin/python
# -*- coding: utf-8 -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 17-05-2017
# @last_modify: Wed May 17 13:01:09 2017
##
########################################


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
	'verbose': {
	    'format': 'LEVEL:%(levelname)s TIME:%(asctime)s MODULE:%(module)s LINE:%(lineno)d PROCESS:%(process)d THREAD:%(thread)d MESSAGE:%(message)s'
	}
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/phoenix.log',
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True
        }
    },
    'loggers': {
        'main': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'critical': {
            'handlers': ['mail_admins', 'file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
