import datetime
import os
import re
import urllib
import urlparse
import uuid

from .mail import ClickLogParser
from apps.adverts.documents import Advert, Impression



class AdvertClickParser(ClickLogParser):

    def __init__(self, filepath, data_directory="/tmp", date_format="%d/%b/%Y",
            primary_tag="click-tracking",
            workers=4, *args, **kwargs):

        super(AdvertClickParser, self).__init__(filepath, data_directory=data_directory,
        date_format=date_format, primary_tag=primary_tag, workers=workers, *args, **kwargs)
        self.data = []
        self.date_regex = r'\d{1,2}\/\w{3}\/\d{4}'

    
    def _prepare(self):
        ## create primary data file
        primary = "%s.log" % uuid.uuid4().__str__()
        primary = os.path.join(self.data_directory, primary)
        os.system('cat %s | grep %s | grep -v _Impression > %s' % (
            self.filepath, self.primary_tag, primary
        ))
        self.primary_data_file = primary

    def _date_hacks(self, date):
            current_year = datetime.datetime.now().year
            date = datetime.datetime.strptime(date, '%d/%b/%Y')
            if (date.date().day == 31 and date.date().month == 12):
                current_year -= 1
            date = date.replace(year=current_year, hour=0, minute=0, second=0)
            return date

    def _parse_message_info(self, line):
        data = {}
        try:
            date = self._date_hacks(re.findall(self.date_regex, line)[0])
            qs_string = re.findall(self.qs_regex, line)
            qs_string = [x for x in qs_string if 'tracking_ID' in x][0]
            qs = urlparse.parse_qs(urllib.unquote(qs_string))
            tracking_id = qs.get('tracking_ID', [None])[0]
            if tracking_id:
                data['date'] = date
                data['tracking_id'] = tracking_id
                data['tracking_source'] = qs.get('tracking_source',[None])[0]
                data['tracking_drive'] = qs.get('tracking_drive', [None])[0]
                data['tracking_medium'] = qs.get('tracking_medium', [None])[0]
                self.data.append(Advert(**data))
            self.prog += 1
            print "%s/%s" % (self.prog, self.total)
        except Exception as err:
            print str(err)
            self.errors += 1


    def update_click_status(self):
        print "Updating advert click status\n"
        Advert.objects.insert(self.data)
        del self.data



class ImpressionsParser(AdvertClickParser):

    def __init__(self, *args, **kwargs):

        super(ImpressionsParser, self).__init__(*args, **kwargs)
        self.data = {}

    def _prepare(self):
        ## create primary data file
        primary = "%s.log" % uuid.uuid4().__str__()
        primary = os.path.join(self.data_directory, primary)
        os.system('cat %s | grep %s | grep _Impression > %s' % (
            self.filepath, self.primary_tag, primary
        ))
        self.primary_data_file = primary


    def _parse_message_info(self, line):
        try:
            date = self._date_hacks(re.findall(self.date_regex, line)[0])
            qs_string = re.findall(self.qs_regex, line)
            qs_string = [x for x in qs_string if 'tracking_ID' in x][0]
            qs = urlparse.parse_qs(urllib.unquote(qs_string))
            tracking_id = qs.get('tracking_ID', [None])[0]
            tracking_source = qs.get('tracking_source',[None])[0]
            tracking_drive = qs.get('tracking_drive', [None])[0]
            tracking_medium = qs.get('tracking_medium', [None])[0]
            
            if tracking_id:

                if not date in self.data:
                    self.data[date] = {}
                date_obj = self.data.get(date)

                if not tracking_id in date_obj:
                    date_obj[tracking_id] = {}
                id_obj = date_obj.get(tracking_id)

                if not tracking_source in id_obj:
                    id_obj[tracking_source] = {}
                src_obj = id_obj.get(tracking_source)

                if not tracking_medium in src_obj:
                    src_obj[tracking_medium] = {}
                med_obj = src_obj.get(tracking_medium)

                if not tracking_drive in med_obj:
                    med_obj[tracking_drive] = {}
                drv_obj = med_obj.get(tracking_drive)

                count = drv_obj.get('count', 0)
                count += 1

                drv_obj['count'] = count
                med_obj[tracking_drive] = drv_obj
                src_obj[tracking_medium] = med_obj
                id_obj[tracking_source] = src_obj
                date_obj[tracking_id] = id_obj
                self.data[date] = date_obj
            self.prog += 1
            print "%s/%s" % (self.prog, self.total)
        except Exception as err:
            print str(err)
            self.errors += 1

    def update_click_status(self):
        print "Updating impressions status\n"

        for dt, dt_obj in self.data.iteritems():
            for tracking_id, id_obj in dt_obj.iteritems():
                for source, src_obj in id_obj.iteritems():
                    for medium, med_obj in src_obj.iteritems():
                        for drive, drv_obj in med_obj.iteritems():
                            count = drv_obj.get('count')
                            Impression.objects.create(date=dt, tracking_id=tracking_id,
                                    tracking_source=source, tracking_medium=medium,
                                    tracking_drive=drive, count=count)
        del self.data
