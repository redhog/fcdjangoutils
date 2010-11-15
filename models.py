import django.db.models
import django.contrib.auth.models
import pinax.apps.tribes.models
import microblogging.models
import pinax.apps.blog.models
import fcdjangoutils.modelhelpers
import django.template
import django.template.loader

# Feeds

class ObjFeed(django.db.models.Model, fcdjangoutils.modelhelpers.SubclasModelMixin):
    class __metaclass__(django.db.models.Model.__metaclass__):
        def __init__(cls, *arg, **kw):
            django.db.models.Model.__metaclass__.__init__(cls, *arg, **kw)
            if cls.__name__ != 'ObjFeed':
                django.db.models.signals.post_save.connect(cls.obj_post_save, sender=cls.owner.field.rel.to)

#    posted_at = django.db.models.DateTimeField(auto_now=True)

    @classmethod
    def obj_post_save(cls, sender, instance, **kwargs):
        # Try around this as OneToOneField are stupid and can't handle null in a sensible way
        try:
            if instance.feed is not None:
                return
        except:
            pass
        cls(owner=instance).save()

    @fcdjangoutils.modelhelpers.subclassproxy
    @property
    def owner(self): raise fcdjangoutils.modelhelpers.MustBeOverriddenError

    def __unicode__(self):
        return "Feed for %s" % (self.owner,)

class UserFeed(ObjFeed):
    owner = django.db.models.OneToOneField(django.contrib.auth.models.User, primary_key=True, related_name="feed")

class TribeFeed(ObjFeed):
    owner = django.db.models.OneToOneField(pinax.apps.tribes.models.Tribe, primary_key=True, related_name="feed")


# Subscriptions

class ObjFeedSubscription(django.db.models.Model):
    feed = django.db.models.ForeignKey(ObjFeed, related_name="subscriptions")

    def is_for(self, feed_entry):
        # Fixme: Some tag stuff here?
        return True

class UserFeedSubscription(ObjFeedSubscription):
    author = django.db.models.ForeignKey(django.contrib.auth.models.User, related_name="subscribed_on_by_feeds")

    def __unicode__(self):
        return "%s subscribes to %s" % (self.feed, self.author)


# Feed entries

class ObjFeedEntry(django.db.models.Model, fcdjangoutils.modelhelpers.SubclasModelMixin):
    class __metaclass__(django.db.models.Model.__metaclass__):
        def __init__(cls, *arg, **kw):
            django.db.models.Model.__metaclass__.__init__(cls, *arg, **kw)
            if cls.__name__ != 'ObjFeedEntry':
                django.db.models.signals.post_save.connect(cls.obj_post_save, sender=cls.obj.field.rel.to)

#    posted_at = django.db.models.DateTimeField(auto_now=True)
    feed = django.db.models.ForeignKey(ObjFeed, related_name="entries")
    author = django.db.models.ForeignKey(django.contrib.auth.models.User, related_name="feed_postings")

    @classmethod
    def obj_post_save(cls, sender, instance, **kwargs):
        if instance.feed_entry is not None:
            return

        author = cls.get_author_from_obj(instance)
        cls(feed=author.feed.superclassobject,
            author = author,
            obj = instance).save()
        for subscription in author.subscribed_on_by_feeds.all():
            feed_entry = cls(feed=subscription.feed.superclassobject,
                             author = author,
                             obj = instance)
            if subscription.is_for(feed_entry):
                feed_entry.save()

    # Very very spartan so it can't break into infinite recursion hell... I.e. DONT't call templates here!!!
    def __repr__(self):
        return "%s: %s posted to %s" % (type(self), self.author, self.feed)

    def __unicode__(self):
        return "%s posted to %s" % (self.render('txt'), self.feed)

    @fcdjangoutils.modelhelpers.subclassproxy
    def get_absolute_url(self):
        return self.obj.get_absolute_url()

    @fcdjangoutils.modelhelpers.subclassproxy
    @property
    def display_name(self):
        return type(self).__name__[:-len('FeedEntry')]        

    template = "djangoobjfeed/render_feed_entry.%(format)s"

    @fcdjangoutils.modelhelpers.subclassproxy
    def render(self, format = 'html'):
        #print "In %s.render for %s" % (type(self), format) 
        #import traceback
        #print traceback.print_stack()
        return django.template.loader.get_template(self.template % {'format':format}
                                                   ).render(django.template.Context({'feed_entry': self}))

# Feed entry adapers

class TweetFeedEntry(ObjFeedEntry):
    obj = django.db.models.ForeignKey(microblogging.models.Tweet, related_name='feed_entry')

    @classmethod
    def get_author_from_obj(cls, obj):
        return obj.sender

    template = "djangoobjfeed/render_tweet_entry.%(format)s"

class BlogFeedEntry(ObjFeedEntry):
    obj = django.db.models.ForeignKey(pinax.apps.blog.models.Post, related_name='feed_entry')

    @classmethod
    def get_author_from_obj(cls, obj):
        return obj.author

    template = "djangoobjfeed/render_blog_entry.%(format)s"
