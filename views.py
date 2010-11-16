import django.http
import django.shortcuts
import djangoobjfeed.models

def post_comment(request, *arg, **kw):    
    comment_on_feed_entry = None
    comment_on_comment = None

    if 'comment_on_feed_entry' in request.POST:
        comment_on_feed_entry = ObjFeedEntry.get(int(request.POST['comment_on_feed_entry']))
        feed = comment_on_feed_entry.feed

    if 'comment_on_comment' in request.POST:
        comment_on_comment = CommentFeedEntry.get(int(request.POST['comment_on_comment']))
        feed = comment_on_comment.feed

    djangoobjfeed.models.CommentFeedEntry(
        author = request.user,
        feed = feed,
        comment_on_feed_entry = comment_on_feed_entry,
        comment_on_comment = comment_on_comment,
        subject = request.POST['subject'],
        content = request.POST['content']
        ).save()

    django.shortcuts.redirect(request.META['HTTP_REFERER'])
