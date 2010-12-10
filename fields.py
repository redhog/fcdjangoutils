import django.forms
import django.utils.safestring
import django.core.urlresolvers
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
