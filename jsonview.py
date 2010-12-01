import sys
import traceback
import django.db.models.base
import django.core.serializers
import django.core.serializers.base
import django.http
import django.utils.simplejson
from jogging import logging
from StringIO import StringIO
from django.db.models.query import QuerySet
import datetime
import django.utils.functional

from fcdjangoutils.timer import Timer

# Hack serialize to include fields from inherited classes too
def _serialize(self, queryset, **options):
    """
    Serialize a queryset.
    """
    self.options = options

    self.stream = options.get("stream", StringIO())
    self.selected_fields = options.get("fields")
    self.use_natural_keys = options.get("use_natural_keys", False)

    self.start_serialization()
    for obj in queryset:
        self.start_object(obj)
        for field in obj._meta.fields: #### <---- Hack is here, was obj._meta.local_fields in django code
            if field.serialize:
                if field.rel is None:
                    if self.selected_fields is None or field.attname in self.selected_fields:
                        self.handle_field(obj, field)
                else:
                    if self.selected_fields is None or field.attname[:-3] in self.selected_fields:
                        self.handle_fk_field(obj, field)
        for field in obj._meta.many_to_many:
            if field.serialize:
                if self.selected_fields is None or field.attname in self.selected_fields:
                    self.handle_m2m_field(obj, field)
        self.end_object(obj)
    self.end_serialization()
    return self.getvalue()

django.core.serializers.base.Serializer.serialize = _serialize

def jsonify_models(obj):
    """default-handler for simplejson dump that serializes Django
    model objects and query sets as well as some other random bits and
    pieces like dates"""
    
    if isinstance(obj, django.db.models.base.Model):
        return django.core.serializers.serialize('python', [obj])[0]
    elif isinstance(obj, QuerySet):
        return django.core.serializers.serialize('python', obj)
    elif isinstance(obj, (datetime.datetime, datetime.date)):
        return str(obj)
    # GAH, Django hides the class for lazy translation strings. I HATE IT SO MUCH!!!
    elif type(obj).__name__ == '__proxy__' and type(obj).__module__ =='django.utils.functional' :
        return obj.encode("utf-8")
    else:
        return obj

def to_json(obj, default=jsonify_models):
    return django.utils.simplejson.dumps(res, default)

def json_view(fn):
    """View decorator for views that return pure JSON"""
    def jsonify(*arg, **kw):
        try:
            res = fn(*arg, **kw)
            if res is None:
                res = {}
        except Exception, e:
            traceback.print_exc()
            res = {'error': {'type': sys.modules[type(e).__module__].__name__ + "." + type(e).__name__,
                             'description': str(e),
                             'traceback': traceback.format_exc()}}
            logging.error("%s: %s" % (str(e), res['error']['type']))
        print "RES", fn.__name__, django.utils.simplejson.dumps(res, default=jsonify_models)
        return django.http.HttpResponse(django.utils.simplejson.dumps(res, default=jsonify_models),
                                        mimetype="text/plain")
    return jsonify

def get_foreign_objects(obj, path):
    foreign = getattr(obj, path[0])
    path = path[1:]

    if hasattr(foreign, "all"):
        foreign = foreign.all()
    else:
        foreign = [foreign]

    for obj in foreign:
        if path:
            for res in get_f|oreign_objects(obj, path):
                yield res
        else:
            yield obj

def expand_foreign_key(objs, foreign_key_col):
    res = {}
    if isinstance(objs, django.db.models.base.Model):
        objs = [objs]
    elif isinstance(objs, QuerySet):
        objs = objs.all()
    for obj in objs:
        for foreign in get_foreign_objects(obj, foreign_key_col.split("__")):
            if foreign is not None:
                res[foreign.pk] = foreign
    return res

def expand_foreign_keys(objs, follow_foreign_keys={}):
    res = {}
    for foreign_key_name, foreign_key_col in follow_foreign_keys.iteritems():
        res[foreign_key_name] = expand_foreign_key(objs, foreign_key_col)
    return res

def get_view(name, cls, follow_foreign_keys={}):
    @json_view
    def get_view(request, *arg, **kw):
        logging.info("Get " + name)
        if 'filter' in request.GET:
            selfs = cls.objects.filter(**django.utils.simplejson.loads(request.GET['filter']))
        else:
            selfs = cls.objects.all()
        if 'order_by' in request.GET:
            selfs = selfs.order_by(*django.utils.simplejson.loads(request.GET['order_by']))

        res = {name: selfs}
        res.update(expand_foreign_keys(selfs, follow_foreign_keys))
        return res
    return get_view
