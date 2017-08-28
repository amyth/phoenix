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

# unzip and filter
gunzip /data/logs/*.gz

for mfile in /data/logs/*; do
    fname=$(echo $mfile | cut -d '/' -f4)
    cat "${mfile}" | grep -w "X-Uid\|X-MailerTag\|removed" > "/data/tmp/${fname}.plog"
    rm "$mfile"
done;
mv /data/tmp/* /data/logs/
echo "Mailer files prepared."
