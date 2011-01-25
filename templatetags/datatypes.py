# Note, this library is free software
# Copyright 2010 FreeCode AS
# Licensed under the MIT license

from django import template
from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.utils import simplejson
import django.db.models.base
import fcdjangoutils.jsonview
from django.utils.safestring import mark_safe
from fcdjangoutils.timer import Timer
import math

register = template.Library()

def nth_filter(value, param):
    try:
        if param not in value:
            return None
        return value[param]
    except:
        return getattr(value, param)

def eachnth_filter(value, param):
    return [nth_filter(part, param) for part in value]

def sum_filter(value):
    return reduce(lambda a,b: a+b, value)

def separateminus_filter(value1, value2):
    if not value1 and not value2:
        return "0"
    res = ''
    if value1:
        res += "%s" % (value1,)
    if value2:
        res += "-%s" % (value2,)
    return res

def aadd_filter(value1, value2):
    return value1 + value2

def jsonify_filter(obj):
    with Timer('jsonify'):
        return mark_safe(simplejson.dumps(obj, default=fcdjangoutils.jsonview.jsonify_models))

def expandforeign_filter(objs, foreign_key_col):
    with Timer('exportforeign'):
        return fcdjangoutils.jsonview.expand_foreign_key(objs, foreign_key_col)

def floor_filter(obj):
    return math.floor(obj)

@register.filter
def handle_none(obj, replacement='-'):
    if obj is None:
        return replacement
    return obj
        

register.filter('expandforeign', expandforeign_filter)
register.filter('jsonify', jsonify_filter)
register.filter('nth', nth_filter)
register.filter('eachnth', eachnth_filter)
register.filter('sum', sum_filter)
register.filter('separateminus', separateminus_filter)
register.filter('aadd', aadd_filter)
register.filter('floor', floor_filter)

