import json
import os
import re
import uuid

from .mail import ClickLogParser
from django.conf import settings



class JobViewParser(ClickLogParser):

    def __init__(self, filepath, data_directory="/tmp", date_format="%d/%b/%Y",
            primary_tag="jid=",
            workers=4, *args, **kwargs):

        super(JobViewParser, self).__init__(filepath, data_directory=data_directory,
        date_format=date_format, primary_tag=primary_tag, workers=workers, *args, **kwargs)
        self.data = {}
        self.date_regex = r'\d{1,2}\/\w{3}\/\d{4}'
        self.filepath

    
    def _prepare(self):
        ## create primary data file
        primary = "%s.log" % uuid.uuid4().__str__()
        primary = os.path.join(self.data_directory, primary)
        os.system('cat %s | grep %s > %s' % (
            self.filepath, self.primary_tag, primary
        ))
        self.primary_data_file = primary

    def _parse_message_info(self, line):
        try:
            jid_data = re.findall(r'&jid=(\d+)', line)
            if jid_data:
                if jid_data[0] in self.data:
                    self.data[jid_data[0]] += 1
                else:
                    self.data[jid_data[0]] = 1
            self.prog += 1
            print "%s/%s" % (self.prog, self.total)
        except Exception as err:
            print str(err)
            self.errors += 1

    def parse_lines(self):
        """
        Parses a single line of log provided.
        """

        with open(self.primary_data_file, 'r') as pd_file:
            lines = pd_file.readlines()
            self.total = len(lines)
            self.prog = 0
            self.errors = 0
            for line in lines:
                self._parse_message_info(line)

        self.write_to_file()

    def write_to_file(self):
        print "Writing job views\n"
        try:
            file_date = re.findall(r'(\d+)', self.filepath)[0]
            file_name = '{}-job-view-counts.json'.format(file_date)
            path = os.path.join(settings.JOBVIEWS_DUMP_PATH, file_name)
            with open(path, 'w') as json_file:
                json_file.write(json.dumps(self.data))
        except Exception as err:
            print str(err), self.filepath
