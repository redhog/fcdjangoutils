from django.db import models

# Only post_save nad pre_save signals are handled as of today
class SignalAutoConnectModel(models.Model):

    class __metaclass__(models.Model.__metaclass__):
        def __init__(cls, *arg, **kw):
            models.Model.__metaclass__.__init__(cls, *arg, **kw)
            if not hasattr(cls, 'Meta') or not getattr(cls.Meta, 'abstract', False):
                for signame in ("pre_save", "post_save"):
                    if hasattr(cls, 'on_'+signame):
                        getattr(models.signals, signame).connect(getattr(cls, 'on_'+signame), sender=cls)

    class Meta:
        abstract = True


