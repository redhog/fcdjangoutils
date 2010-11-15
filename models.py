import django.db.models
import django.contrib.auth.models
import pinax.apps.tribes.models
import microblogging.models
import pinax.apps.blog.models
import utils.modelhelpers

# Feeds

class ObjFeed(django.db.models.Model, utils.modelhelpers.SubclasModelMixin):
    @utils.modelhelpers.subclassproxy
    @property
    def owner(self): raise utils.modelhelpers.MustBeOverriddenError

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

class ObjFeedEntry(django.db.models.Model, utils.modelhelpers.SubclasModelMixin):
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

    def __unicode__(self):
        return "%s posted to %s" % (self.to_string(), self.feed)

    @utils.modelhelpers.subclassproxy
    def get_absolute_url(self):
        return self.obj.get_absolute_url()

    @utils.modelhelpers.subclassproxy
    @property
    def display_name(self):
        return type(self).__name__[:-len('FeedEntry')]

    @utils.modelhelpers.subclassproxy
    def header_to_string(self):
        return "[%s by %s]" % (self.display_name, self.author)

    @utils.modelhelpers.subclassproxy
    def header_to_html(self):
        return "<a href='%s'>%s</a> by <a href='%s'>%s</a>" % (self.get_absolute_url(), self.display_name, self.author.get_absolute_url(), self.author)

    @utils.modelhelpers.subclassproxy
    def header_to_rss(self):
        return self.header_to_string()

    @utils.modelhelpers.subclassproxy
    def to_string(self): raise utils.modelhelpers.MustBeOverriddenError

    @utils.modelhelpers.subclassproxy
    def to_html(self):
        return self.to_string()

    @utils.modelhelpers.subclassproxy
    def to_rss(self):
        return self.to_string()

# Feed entry adapers

class TweetFeedEntry(ObjFeedEntry):
    obj = django.db.models.ForeignKey(microblogging.models.Tweet, related_name='feed_entry')

    @classmethod
    def get_author_from_obj(cls, obj):
        return obj.sender

    def to_string(self):
        return self.obj.text

    def to_html(self):
        return self.to_string()

class BlogFeedEntry(ObjFeedEntry):
    obj = django.db.models.ForeignKey(pinax.apps.blog.models.Post, related_name='feed_entry')

    @classmethod
    def get_author_from_obj(cls, obj):
        return obj.author

    def to_string(self):
        return self.obj.title + ": " + self.obj.tease

    def to_html(self):
        return "%s<br />%s" % (self.obj.title, self.obj.tease)
