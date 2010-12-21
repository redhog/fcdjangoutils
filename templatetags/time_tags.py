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

register = template.Library()

@register.filter
def duration(duration):
    return '%d:%02d' % (duration/60, duration%60)

