import re

from datetime import datetime
from django.db import models
from django.contrib.auth.models import User

from markdown import markdown
from django.template.defaultfilters import slugify
from django.utils.text import truncate_html_words, truncate_words
from django.db.models.signals import post_save


# regex used to find links in an article
LINK_RE = re.compile('<a.*?href="(.*?)".*?>(.*?)</a>', re.I|re.M)
TITLE_RE = re.compile('<title.*?>(.*?)</title>', re.I|re.M)
TAG_RE = re.compile('[^a-z0-9\-_\+\:\.]?', re.I)

class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.CharField(max_length=64, unique=True, null=True, blank=True)

    def __unicode__(self):
        return self.name

    @staticmethod
    def clean_tag(name):
        """replace spaces with dashes, in man-made slugs"""

        name = name.replace(' ', '-').encode('ascii', 'ignore')
        name = TAG_RE.sub('', name)
        clean = name.lower().strip(", ")
        return clean

    def save(self, *args, **kwargs):
        """methods to be run before post is saved"""

        self.slug = Tag.clean_tag(self.name)
        super(Tag, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('articles_display_tag', (self.slug,))

    @property
    def rss_name(self):
        return self.slug

    class Meta:
        ordering = ('name',)



class PostManager(models.Manager):

    def active(self, user=None):
        """retrieves non-draft articles that have past their publish_date"""

        now = datetime.now()
        if user is not None and user.is_superuser:
            # superusers get to see all articles, reguardless of draft-status
            return self.get_query_set().filter(publish_date__lte=now)
        else:
            # only show published, non-draft articles to visitors
            return self.get_query_set().filter(
                publish_date__lte=now,
                draft_mode=False)


class Post(models.Model):

    # datefields
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    publish_date = models.DateTimeField(default=datetime.now,
        help_text=('The date and time this article will be published.'))

    # metadata
    keywords = models.CharField(max_length=250, blank=True,
        help_text="A concise list of items and terms that describe the \
                    content of the post.<br /> If omitted, keywords will the \
                    same as the tags for the post. Used by search engines.")
    description = models.TextField(blank=True,
        help_text="A brief explanation of the post's content used by search \
                    engines. (auto-magic)")
    # editable fields
    title = models.CharField(max_length=250)
    content = models.TextField()
    excerpt = models.TextField(blank=True,
        help_text='A short teaser of your posts content. If omitted, an excerpt\
         will be generated from the content field. (auto-magic)')

    slug = models.SlugField(unique_for_year='publish_date',
        help_text='A URL-friendly representation of your posts title.')

    tags = models.ManyToManyField(Tag, blank=True,
        help_text='Tags that describe this article. Select from existing tags \
                    or create new tags. <br />')

    draft_mode = models.BooleanField(default=False,
        help_text='Posts in draft-mode will not appear to regular users.')

    # hidden fields
    rendered_content = models.TextField()
    rendered_excerpt = models.TextField()
    author = models.ForeignKey(User, related_name="posts")

    # custom manager
    objects = PostManager()

    def __init__(self, *args, **kwargs):

        super(Post, self).__init__(*args, **kwargs)
        self._excerpt = None

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """overwrite model.save to call our new methods before saving."""

        self.render_content()
        self.render_excerpt()
        self.meta_description()

        super(Post, self).save(*args, **kwargs)

        requires_save = self.tags_to_keywords()

        if requires_save:
            # bypass the other processing
            super(Post, self).save()

    def render_content(self):
        """renders markdown in post.content to post.rendered_content"""

        original = self.rendered_content
        self.rendered_content = markdown(self.content)

        return (self.rendered_content != original)

    def meta_description(self):
        """if meta description is empty, sets it to the article's excerpt"""

        if len(self.description.strip()) == 0:
            self.description = truncate_words(self.content, 25)
            return True

        return False

    def render_excerpt(self):
        """if excerpt is blank, we create it from post.content"""

        if len(self.excerpt.strip()):
            self.rendered_excerpt = markdown(self.excerpt)
        else:
            self.excerpt = truncate_words(self.content, 60)
            self.rendered_excerpt = markdown(self.excerpt)

        return self.excerpt

    def tags_to_keywords(self):
        """
        If meta keywords is empty, sets them using the posts tags.

        Returns True if an additional save is required, False otherwise.
        """

        if len(self.keywords.strip()) == 0:
            self.keywords = ', '.join([t.name for t in self.tags.all()])
            return True

        return False

    @models.permalink
    def get_absolute_url(self):
        return ('articles_display_article', (self.publish_date.year, self.slug))

    class Meta:
        ordering = ('-publish_date', 'title')
        get_latest_by = 'publish_date'