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
from django.utils.translation import ugettext_lazy as _

import math

register = template.Library()

@register.filter
def duration(duration):
    return '%d:%02d' % (duration/60, duration%60)

@register.filter
def duration_diff(dd):
    if dd == 0:
        return _("No change")
    if dd > 0:
        suffix = _("better")
    else:
        suffix  = _('worse')

    dd = math.abs(dd)
    res = ""
    if dd > 60:
        res += _("%d minutes") % (dd/60)
    res += _("%d seconds") % (dd%60)

    res += " " + suffix
    return res
