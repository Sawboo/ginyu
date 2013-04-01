import re

from datetime import datetime
from django.db import models
from django.contrib.auth.models import User

import markdown2
from django.utils.text import truncate_words, truncate_html_words


class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.CharField(max_length=64, unique=True, null=True, blank=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('articles_display_tag', (self.slug,))

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

    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    publish_date = models.DateTimeField(default=datetime.now,
                                        help_text=('The date and time this \
                                            article will be published.'))
    description = models.TextField(blank=True,
                                   help_text="A brief explanation of the \
                                   post's content used by search engines. \
                                   (auto-magic)")
    title = models.CharField(max_length=250)
    content = models.TextField()
    rendered_content = models.TextField()
    excerpt = models.TextField(blank=True,
                               help_text='A short teaser of your posts \
                               content. If omitted, an excerpt will be \
                               generated from the content field. (auto-magic)')
    rendered_excerpt = models.TextField()
    slug = models.SlugField(unique_for_year='publish_date',
                            help_text='A URL-friendly representation of your \
                            posts title.')
    tags = models.ManyToManyField(Tag, blank=True,
                                  help_text='Tags that describe this article. \
                                  Select from existing tags or create new \
                                  tags. <br />')
    draft_mode = models.BooleanField(default=False,
                                     help_text='Posts in draft-mode will not \
                                     appear to regular users.')
    author = models.ForeignKey(User, related_name="posts")

    # add our custom manager
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

    def render_content(self):
        """render post.rendered_content from post.content"""

        self.rendered_content = render_markup(self.content)
        return self.rendered_content

    def render_excerpt(self):
        """renders post.rendered_excerpt. If excerpt is blank, create it"""

        if len(self.excerpt.strip()):
            self.rendered_excerpt = render_markup(self.excerpt)
        else:
            # use truncate_html_words to preserve linebreaks in self.content
            self.excerpt = truncate_html_words(self.content, 80)
            self.rendered_excerpt = render_markup(self.excerpt)
        return self.excerpt

    def meta_description(self):
        """if meta description is empty, create it from post.content"""

        if len(self.description.strip()) == 0:
            self.description = truncate_words(self.content, 25)
        return self.description

    @models.permalink
    def get_absolute_url(self):
        return ('articles_display_article',
                (self.publish_date.year, self.slug))

    class Meta:
        ordering = ('-publish_date', 'title')
        get_latest_by = 'publish_date'


def render_markup(markdown):
    """
    Uses markdown2 to return html markup.

    Extra implementations include:
        * fenced-code-blocks with syntax highlighting.
            http://github.com/trentm/python-markdown2/wiki/fenced-code-blocks
        * wiki-tables support.
            http://github.com/trentm/python-markdown2/wiki/wiki-tables
    """

    markup = markdown2.markdown(markdown, extras=[
        "fenced-code-blocks",
        "wiki-tables",
        "code-friendly"])
    return markup
