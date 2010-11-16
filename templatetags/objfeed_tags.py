import django.template

register = django.template.Library()

@register.inclusion_tag("djangoobjfeed/objfeed.html")
def objfeed_for_user(user, is_me):
    return {"feed": user.feed}

@register.inclusion_tag("djangoobjfeed/objfeed.html")
def objfeed_for_tribe(tribe):
    return {"feed": tribe.feed}

class RenderNode(django.template.Node):
    def __init__(self, entry, format):
        self.entry = django.template.Variable(entry)
        self.format = django.template.Variable(format)

    def render(self, context):
        return self.entry.resolve(context).render(self.format.resolve(context), context)

@register.tag
def render(parser, token):
    try:
        tag_name, entry, format = token.split_contents()
    except ValueError:
        raise django.template.TemplateSyntaxError, "%r tag requires two arguments" % token.contents.split()[0]
    return RenderNode(entry, format)
