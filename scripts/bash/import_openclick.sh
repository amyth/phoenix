#!/bin/bash
#
#baseDir="/root/ascripts/adashview"
#cd ${baseDir}

Yesterday=$(date --date='1 days ago' '+%Y%m%d')

logServer="172.22.65.10"
openServer="172.22.65.135"

apacheLogFileOrg="/var/log/httpd-access/httpd-access.log-${Yesterday}"
openLogFile="/var/log/nginx/trackOpen.log-${Yesterday}"

# copy from log server
scp root@${logServer}:${apacheLogFileOrg} /data/logs/
scp root@${openServer}:${openLogFile} /data/logs/
