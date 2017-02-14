from django.conf import settings

import rules

@rules.predicate
def is_allowed_campaign(user, campaign):
    user_group = user.groups.first()
    if user_group:
        campaigns = settings.CAMPAIGN_PERMISSIONS.get(user_group.name, [])

        if campaign in campaigns:
            return True

        if '*' in campaigns:
            return True

    return False


try:
    rules.add_rule('is_allowed_campaign', is_allowed_campaign)
except KeyError as err:
    pass
