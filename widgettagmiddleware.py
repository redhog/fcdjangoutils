import threading
import re

class WidgetTagMiddleware(object):
    data = threading.local()
    var_re = re.compile(r'%WidgetTagMiddleware.([^%]*)%')

    def process_request(self, request):
        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        return None

    def process_response(self, request, response):
        if 'text/' in response['Content-Type']:
            for name, values in getattr(self.data, 'vars', {}).iteritems():
                response.content = response.content.replace('%WidgetTagMiddleware.'+name+'%', ''.join(values.itervalues()))
            response.content = self.var_re.sub('', response.content)
        return response

    def process_exception(self, request, exception):
        return None

    @classmethod
    def _ensure(cls):
        if getattr(cls.data, 'vars', None) is None:
            cls.data.vars = {}

    @classmethod
    def add(cls, section, key, value):
        cls._ensure()
        if section not in cls.data.vars:
            cls.data.vars[section] = {}
        cls.data.vars[section][key] = value

    @classmethod
    def addjs(cls, filename):
        cls.add("head.javascript", filename, "<script language='javascript' type='text/javascript' src='%s'></script>" % (filename,))

    @classmethod
    def addcss(cls, filename):
        cls.add("head.css", filename, "<link rel='stylesheet' type='text/css' href='%s' />" % (filename,))

    @classmethod
    def adddialog(cls, name, html):
        cls.add("body.dialog", name, "<div id='%s'>%s<div>" % (name, html))
