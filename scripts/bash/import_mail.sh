#!/bin/bash
#
#baseDir="/root/ascripts/adashview"
#cd ${baseDir}

Yesterday=$(date --date='1 days ago' '+%Y%m%d')
tmpFile="/data/mail.log"


logServer="172.22.65.10"
netMagicSMTPLogFileOrg="/var/log/smtp/mail.log-"${Yesterday}"*"
amazonSMTPLogFileOrg=$(ssh -l root ${logServer} "ls -tr /awssmtplogs/maillog* | tail -n 1")

# copy from log server
scp root@${logServer}:${netMagicSMTPLogFileOrg} /data/logs/
scp root@${logServer}:${amazonSMTPLogFileOrg} /data/logs/
