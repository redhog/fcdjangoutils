import django.template

register = django.template.Library()

@register.inclusion_tag("objfeed.html")
def objfeed_for_user(user, is_me):
    return {"feed": user.feed}

@register.inclusion_tag("objfeed.html")
def objfeed_for_tribe(tribe):
    return {"feed": tribe.feed}
