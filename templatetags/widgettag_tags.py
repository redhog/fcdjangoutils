import fcdjangoutils.widgettagmiddleware
import django.template

register = django.template.Library()


class AddRenderer(django.template.Node):
    def __init__(self, fn, filename):
        self.fn = fn
        self.filename = django.template.Variable(filename)

    def render(self, context):
        self.fn(self.filename.resolve(context))
        return ''

@register.tag
def widget_addjs(parser, token):
    try:
        tag_name, filename = token.split_contents()
    except ValueError:
        raise django.template.TemplateSyntaxError, "%r tag requires one arguments" % token.contents.split()[0]
    return AddRenderer(fcdjangoutils.widgettagmiddleware.WidgetTagMiddleware.addjs, filename)

@register.tag
def widget_addcss(parser, token):
    try:
        tag_name, filename = token.split_contents()
    except ValueError:
        raise django.template.TemplateSyntaxError, "%r tag requires one arguments" % token.contents.split()[0]
    return AddRenderer(fcdjangoutils.widgettagmiddleware.WidgetTagMiddleware.addcss, filename)

