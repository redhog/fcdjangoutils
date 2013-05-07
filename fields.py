# -*- coding: utf-8 -*-
import django.forms
import django.utils.safestring
import django.core.urlresolvers
import StringIO
from django.utils.simplejson import dumps, loads, JSONEncoder
import dateutil.parser
import datetime
import django.db.models
import django.utils.functional
import django.db
import django.db.models.query
try:
    import idmapper.models
except:
    pass
import base64
import jsonview
from django.utils.translation import ugettext_lazy as _

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

class JsonFormField(django.forms.Field):
    default_error_messages = {
        'invalid': _(u'Enter a valid JSON expression.'),
    }

    def __init__(self, *args, **kwargs):
        super(JsonFormField, self).__init__(*args, **kwargs)

    def prepare_value(self, value):
        if value is None:
            value = ""
        elif not isinstance(value, (str, unicode)):
            value = jsonview.to_json(value)
        return super(JsonFormField, self).prepare_value(value)

    def to_python(self, value):
        value = super(JsonFormField, self).to_python(value).strip()
        if not value: return None
        return jsonview.from_json(value)

class JsonField(django.db.models.Field): 
    __metaclass__ = django.db.models.SubfieldBase 
    serialize_to_string = True 
    def get_internal_type(self): 
        return "TextField" 
    def value_to_string(self, obj): 
        return self.get_prep_value(self._get_val_from_obj(obj)) 
    def get_prep_value(self, value):
        return jsonview.to_json(value) 
    def to_python(self, value):
        if isinstance(value, (str, unicode)):
            if not value.strip():
                return None
            return jsonview.from_json(value)
        return value 
    def formfield(self, **kwargs):
        kwargs['form_class'] = JsonFormField
        return super(JsonField, self).formfield(**kwargs)

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


class WeakForeignKeyDescriptor(object):
    def __init__(self, related):
        self.related = related

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self

        return self.related_manager_cls(instance)

    def __set__(self, instance, value):
        raise ValueError("WeakForeignKey does not support assignement; Assign to the value fields used to define it instead.")


    @django.utils.functional.cached_property
    def related_manager_cls(self):
        # Dynamically create a class that subclasses the related model's default
        # manager.
        superclass = self.related.model._default_manager.__class__
        related_object_descriptor = self

        class RelatedManager(superclass):
            def __init__(self, instance):
                super(RelatedManager, self).__init__()
                self.core_filters = {'%s__exact' % related_object_descriptor.related.related_field.name:
                                         getattr(instance, related_object_descriptor.related.db_column)}
                self.instance = instance

            def get_queryset(self, **db_hints):
                db = django.db.router.db_for_read(related_object_descriptor.related.rel.to, **db_hints)
                return django.db.models.query.QuerySet(related_object_descriptor.related.rel.to).using(db).filter(**self.core_filters)

        return RelatedManager

class WeakForeignKey(django.db.models.ForeignKey):
    """Defines a weak, or fake, foreign key based on an existing field.
    You must set db_column (and probably want to set to_field too).
    Usefull to construct joins on non-primary keys."""

    requires_unique_target=False

    def __init__(self, to, db_constraint=False, null=True, blank=True, *arg, **kw):
        django.db.models.ForeignKey.__init__(self, to, db_constraint=db_constraint, null=null, blank=blank, *arg, **kw)

    def db_type(self, connection):
        return None

    def contribute_to_class(self, cls, name, virtual_only=False):
        super(WeakForeignKey, self).contribute_to_class(cls, name, virtual_only=virtual_only)
        self.field = self
        setattr(cls, self.name, WeakForeignKeyDescriptor(self))

    def validate(self, value, model_instance):
        # Did I say this is a weak foreign key? It can't fail...
        pass
