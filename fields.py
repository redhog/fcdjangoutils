# -*- coding: utf-8 -*-
import django.forms
import django.utils.safestring
import django.core.urlresolvers
import StringIO
from django.utils.simplejson import dumps, loads, JSONEncoder
import dateutil.parser
import datetime
import django.db.models
import idmapper.models
import base64

class ModelLinkWidget(django.forms.Select):
    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            return ''
        if hasattr(value, 'all'):
            value = value.all()
        elif not isinstance(value, (list, tuple)):
            value = [value]
        lines = ("<a href='%s'>%s</a>" % (django.core.urlresolvers.reverse('admin:%s_%s_change' % (type(obj)._meta.app_label, type(obj)._meta.module_name), args=(obj.id,)), obj)
                 for obj in value)
        out = "<ul>%s</ul>" % ('\n'.join("<li>%s</li>" % (line,) for line in lines))
        return django.utils.safestring.mark_safe(unicode(out))

class ModelLinkField(django.forms.ModelChoiceField):
    widget = ModelLinkWidget

class JsonField(django.db.models.Field): 
    __metaclass__ = django.db.models.SubfieldBase 
    serialize_to_string = True 
    def get_internal_type(self): 
        return "TextField" 
    def value_to_string(self, obj): 
        return self.get_prep_value(self._get_val_from_obj(obj)) 
    def get_prep_value(self, value):
        stream = StringIO.StringIO() 
        django.utils.simplejson.dump(value, stream, default=self.json_encoder) 
        value = stream.getvalue() 
        stream.close() 
        return value 
        #~ return None 
    def to_python(self, value): 
        if isinstance(value, (str, unicode)): 
            value = StringIO.StringIO(value) 
            return django.utils.simplejson.load(value, object_hook=self.json_decoder) 
        return value 
    def json_encoder(self, value):
        if type(value) is datetime.date:
            return {"__jsonclass__": ["datetime.date"], "value": value.isoformat()}
        elif type(value) is datetime.datetime:
            return {"__jsonclass__": ["datetime.datetime"], "value": value.isoformat()}
        else:
            return value
    def json_decoder(self, value):
        if "__jsonclass__" in value:
            if value["__jsonclass__"][0] == "datetime.date":
                value = dateutil.parser.parse(value['value']).date()
            elif value["__jsonclass__"][0] == "datetime.datetime":
                value = dateutil.parser.parse(value['value'])
        return value

class Base64Field(django.db.models.TextField):
    def contribute_to_class(self, cls, name):
        if self.db_column is None:
            self.db_column = name
        self.field_name = name + '_base64'
        super(Base64Field, self).contribute_to_class(cls, self.field_name)
        setattr(cls, name, property(self.get_data, self.set_data))

    def get_data(self, obj):
        return base64.decodestring(getattr(obj, self.field_name))

    def set_data(self, obj, data):
        setattr(obj, self.field_name, base64.encodestring(data))
