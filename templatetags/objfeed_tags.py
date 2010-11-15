import django.template

register = django.template.Library()

def render_filter(obj, format = 'html'):
    return obj.render(format)

register.filter('render', render_filter)

@register.inclusion_tag("djangoobjfeed/objfeed.html")
def objfeed_for_user(user, is_me):
    return {"feed": user.feed}

@register.inclusion_tag("djangoobjfeed/objfeed.html")
def objfeed_for_tribe(tribe):
    return {"feed": tribe.feed}
