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

class JsonDecodeRegistry(object):
    registry = {}

    @classmethod
    def register(cls, class_hint):
        def register(fn):
            cls.registry[class_hint] = fn
        return register

    @classmethod
    def objectify(cls, obj):
        # FIXME: Is there a better/faster way to do this using sets?
        for key, fn in cls.registry.iteritems():
            if key in obj:
                return fn(obj)
        return obj

class JsonEncodeRegistry(object):
    registry = []

    @classmethod
    def register(cls, instof=None, test=None):
        if test is None:
            def test(obj):
                return isinstance(obj, instof)
        def register(fn):
            cls.registry[0:0] = [(test, fn)]
        return register

    @classmethod
    def jsonify(cls, obj):
        for test, conv in cls.registry:
            if test(obj):
                return conv(obj)
        return obj

@JsonEncodeRegistry.register(django.db.models.base.Model)
def modelconv(obj):
    return type(obj).objects.values().get(id=obj.id)

@JsonEncodeRegistry.register(QuerySet)
def modelconv(obj):
    return list(obj.values())

@JsonEncodeRegistry.register((datetime.datetime, datetime.date))
def modelconv(obj):
    return str(obj)

def modeltest(obj):
    # GAH, Django hides the class for lazy translation strings. I HATE IT SO MUCH!!!
    return type(obj).__name__ == '__proxy__' and type(obj).__module__ =='django.utils.functional'
@JsonEncodeRegistry.register(test=modeltest)
def modelconv(obj):
    return obj.encode("utf-8")

#jsonify_models = JsonEncodeRegistry.jsonify

def from_json(jsonstr, objectify=JsonDecodeRegistry.objectify):
    return django.utils.simplejson.loads(jsonstr, object_hook=objectify)

def to_json(obj, jsonify=JsonEncodeRegistry.jsonify):
    return django.utils.simplejson.dumps(obj, default=jsonify)

def json_view(fn):
    """View decorator for views that return pure JSON"""
    def jsonify(*arg, **kw):
        try:
            res = fn(*arg, **kw)
            if res is None:
                res = {}
        except django.core.servers.basehttp.WSGIServerException:
            raise
        except Exception, e:
            traceback.print_exc()
            res = {'error': {'type': sys.modules[type(e).__module__].__name__ + "." + type(e).__name__,
                             'description': str(e),
                             'traceback': traceback.format_exc()}}
            logging.error("%s: %s" % (str(e), res['error']['type']))
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
