#!/bin/bash
#
#baseDir="/root/ascripts/adashview"
#cd ${baseDir}

if [ -z "$1" ]; then
    Yesterday=$(date --date='1 days ago' '+%Y%m%d')
else
    Yesterday=$1
fi
#Yesterday="20161101"
tmpFile="/data/mail.log"


logServer="172.22.65.10"
netMagicSMTPLogFileOrg="/var/log/smtp/mail.log-"${Yesterday}"*"

if [ -z "$2" ]; then
    amazonSMTPLogFileOrg=$(ssh -l root ${logServer} "ls -tr /awssmtplogs/maillog* | tail -n 1")
else
    amazonSMTPLogFileOrg="/awssmtplogs/maillog-$2_*"
fi

# copy from log server
scp root@${logServer}:${netMagicSMTPLogFileOrg} /data/logs/
scp root@${logServer}:${amazonSMTPLogFileOrg} /data/logs/
