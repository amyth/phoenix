#!/bin/bash
#
#baseDir="/root/ascripts/adashview"
#cd ${baseDir}

if [ -z "$1" ]; then
    Yesterday=$(date --date='1 days ago' '+%Y%m%d')
else
    Yesterday=$1
fi

#logServer="172.22.65.10"
openServer="172.22.65.135"

#apacheLogFileOrg="/var/log/httpd-access/httpd-access.log-${Yesterday}*"
#apacheRecruiterLogFileOrg="/var/log/httpd-access/httpd-recruiter-access.log-${Yesterday}*"
openLogFile="/var/log/nginx/mylogger.log-${Yesterday}*"

# copy from log server
#scp root@${logServer}:${apacheLogFileOrg} /data/logs/
#scp root@${logServer}:${apacheRecruiterLogFileOrg} /data/logs/
scp root@${openServer}:${openLogFile} /data/logs/
