# -*- coding: utf-8 -*-
import django.db.models.fields.related
import django.db.models
import idmapper.models
import base64

class SubclasModelMixin(object):
    @classmethod
    def get_model_subclass_relations(cls):
        res = {}
        for name in dir(cls):
            try:
                attr = getattr(cls, name)
            except:
                attr = None
            if isinstance(attr, django.db.models.fields.related.SingleRelatedObjectDescriptor) and issubclass(attr.related.model, cls) and cls is not attr.related.model:
                res[name] = attr.related.model
        return res

    @classmethod
    def get_model_superclass_relations(cls):
        res = {}
        for name in dir(cls):
            try:
                attr = getattr(cls, name)
            except:
                attr = None
            if isinstance(attr, django.db.models.fields.related.ReverseSingleRelatedObjectDescriptor) and issubclass(cls, attr.field.rel.to) and cls is not attr.field.rel.to:
                res[name] = attr.field.rel.to
        return res

    @property
    def subclassobject(self):
        for name in self.get_model_subclass_relations().iterkeys():
            # Use try around this since Django throws DoesNotExist instead of AttributeError... Bah!
            try:
                value = getattr(self, name, None)
            except:
                value = None
            if value is not None:
                return value
        return self

    @property
    def superclassobject(self):
        for name in self.get_model_superclass_relations().iterkeys():
            # Use try around this since Django throws DoesNotExist instead of AttributeError... Bah!
            try:
                value = getattr(self, name)
            except:
                value = None
            if value is not None:
                return value
        return self

class MustBeOverriddenError(Exception):
    pass

def subclassproxy(fn):
    is_property = isinstance(fn, property)
    if is_property:
        fn = fn.fget

    name = fn.func_name

    def proxy(self, *arg, **kw):
        if self.subclassobject is self:
            try:
                return fn(self, *arg, **kw)
            except MustBeOverriddenError:
                try:
                    strrepr = unicode(self)
                except:
                    strrepr = id(self)
                raise NotImplementedError("%s.%s is a subclass proxy, but %s is not an instance of a subclass that overides it" % (type(self), name, strrepr))
        res = getattr(self.subclassobject, name)
        if not is_property:
            res = res(*arg, **kw)
        return res

    if is_property:
        proxy = property(proxy)
    return proxy

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
