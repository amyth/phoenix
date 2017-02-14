from django.conf import settings

from rules import predicate


@predicate
def is_allowed_campaign(user, campaign):
    user_group = user.groups.first()
    campaigns = settings.CAMPAIGN_PERMISSIONS.get(user_group.name, [])

    if campaign in campaigns:
        return True

    if '*' in campaigns:
        return True

    return False
