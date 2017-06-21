import mongoengine


class Advert(mongoengine.Document):
    """ Represents an advert object.
    """

    date = mongoengine.DateTimeField()
    tracking_source = mongoengine.StringField()
    tracking_drive = mongoengine.StringField()
    tracking_medium = mongoengine.StringField()
    tracking_id = mongoengine.StringField()
    image_url_identifier = mongoengine.StringField()

    @property
    def logo_image(self):
        if self.image_url_identifier:
            static_path = "https://static2.shine.com/media1/images/employerbranding/"
            return "{}{}".format(static_path, self.image_url_identifier)
        return None


class Impression(mongoengine.Document):
    """ Represents as impression object.
    """

    date = mongoengine.DateTimeField()
    tracking_source = mongoengine.StringField()
    tracking_drive = mongoengine.StringField()
    tracking_medium = mongoengine.StringField()
    tracking_id = mongoengine.StringField()
    count = mongoengine.IntField(default=0)
