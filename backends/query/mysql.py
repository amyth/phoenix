#!/usr/bin/python
# -*- coding: utf-8 -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 11-05-2017
# @last_modify: Thu May 11 17:39:46 2017
##
########################################



CREATE_SENT_TABLE = """
    CREATE TABLE IF NOT EXISTS %s (
	sno INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	user_email CHAR(128) NULL,
	from_email CHAR(128) NULL,
	reply_email CHAR(128) NULL,
	action_date DATETIME NULL,
	job_id CHAR(128) NULL,
	job_score CHAR(128) NULL,
	subject CHAR(255) NULL,
	recruiter_id CHAR(128) NULL,
	campaign CHAR(255) NULL,
	campaign_date DATETIME NULL,
	campaign_id CHAR(128) NULL) ENGINE=MyISAM DEFAULT CHARACTER SET=utf8;
"""


CREATE_OPEN_TABLE = """
    CREATE TABLE IF NOT EXISTS %s (
	sno INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	user_email CHAR(128) NULL,
	action_date DATETIME NULL,
	job_id CHAR(128) NULL,
	job_score CHAR(128) NULL,
	device CHAR(255) NULL,
	recruiter_id CHAR(128) NULL,
	campaign CHAR(255) NULL,
	campaign_date DATETIME NULL,
	campaign_id CHAR(128) NULL) ENGINE=MyISAM DEFAULT CHARACTER SET=utf8;
"""


CREATE_CLICK_TABLE = """
    CREATE TABLE IF NOT EXISTS %s (
	sno INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	user_email CHAR(128) NULL,
	action_date DATETIME NULL,
	job_id CHAR(128) NULL,
	job_score CHAR(128) NULL,
	device CHAR(255) NULL,
	recruiter_id CHAR(128) NULL,
	primary_action BOOLEAN NOT NULL DEFAULT 0,
	endpoint CHAR(255) NULL,
	campaign CHAR(255) NULL,
	campaign_date DATETIME NULL,
	campaign_id CHAR(128) NULL) ENGINE=MyISAM DEFAULT CHARACTER SET=utf8;
"""
