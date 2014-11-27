from django.db.models.signals import post_save


def auto_keywords(sender, instance, signal,
    *args, **kwargs):
    """
    If meta-keywords are left blank on post.save(), they will be
    copied from the posts tags.
    """

    if len(instance.keywords.strip()) == 0:
        from hikari.ginyu.models import Post
        post_save.disconnect(auto_keywords, sender=Post)
        instance.keywords = ', '.join([t.name for t in instance.tags.all()])
        instance.save()
        post_save.connect(auto_keywords, sender=Post)

post_save.connect(auto_keywords, sender=Post)
