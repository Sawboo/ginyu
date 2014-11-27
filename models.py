from django.db import models
from django.contrib.auth.models import User
from django.utils.html import strip_tags
from django.utils.text import Truncator
from datetime import datetime
from django.utils.timezone import utc

import requests
import json

def render_markup(markdown):
    """
    Uses the github api to return html markup.

    """
    headers = {'content-type': 'application/json'}

    context = {
        "text": markdown,
        "mode": "gfm",
        "context": "github/sawboo"
    }

    r = requests.post('https://api.github.com/markdown', data=json.dumps(context), headers=headers)

    return r.text


class Tag(models.Model):
    """
    A simple model used to categorize Post objects.

    """
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
    """
    A custom manager for the Post model.

    Define shortcut methods for making database querys.

    """
    def active(self, user=None):
        """
        Retrieve non-draft posts that have past their publish_date.

        """
        now = datetime.utcnow().replace(tzinfo=utc)
        return self.get_query_set().filter(
            publish_date__lte=now, draft_mode=False)


class Post(models.Model):
    """
    A model that stores data related to a single blog post.

    """
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    publish_date = models.DateTimeField(default=datetime.utcnow().replace(tzinfo=utc),
                                        help_text=('The date and time this \
                                            article will be published.'))
    content = models.TextField()
    rendered_content = models.TextField()
    rendered_excerpt = models.TextField()
    excerpt = models.TextField(blank=True,
                               help_text='A short teaser of your posts \
                               content. If omitted, an excerpt will be \
                               generated from the content field. (auto-magic)')
    description = models.TextField(blank=True,
                                   help_text="A brief explanation of the \
                                   post's content used by search engines. \
                                   (auto-magic)")
    slug = models.SlugField(unique_for_year='publish_date',
                            help_text='A URL-friendly representation of your \
                            posts title.')
    tags = models.ManyToManyField(Tag, blank=True,
                                  help_text='Tags that describe this article. \
                                  Select from existing tags or create new \
                                  tags. <br />')
    html_mode = models.BooleanField(default=False,
                                    help_text='Posts in html-mode will not be \
                                    rendered using Markdown.')
    draft_mode = models.BooleanField(default=False,
                                     help_text='Posts in draft-mode will not \
                                     appear to regular users.')
    author = models.ForeignKey(User, related_name="posts")

    # attach our custom manager
    objects = PostManager()

    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)

        self._excerpt = None
        self._next = None
        self._previous = None

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Call required methods before saving.

        """
        self.render_content()
        self.meta_description()

        # If the excerpt is left blank it will be generated from
        # `self.content`, possibly resulting in open markdown tags.
        # We can still generate a proper `self.rendered_excerpt` by
        # html truncating `self.rendered_content`. Before calling
        # the save method, check to see if `self.excerpt` has
        # changed before rendering it.
        try:
            original = Post.objects.get(pk=self.pk)
            if original.excerpt != self.excerpt:
                self.render_excerpt()
        except Post.DoesNotExist:
            self.render_excerpt()

        super(Post, self).save(*args, **kwargs)

    def render_content(self):
        """
        Use markdown2 to render post.rendered_content from post.content.

        """
        if self.html_mode == False:
            self.rendered_content = render_markup(self.content)
        else:
            self.rendered_content = self.content
        return self.rendered_content

    def render_excerpt(self):
        """
        If self.excerpt is blank generate it from `self.content`.
        Otherwise, render self.rendered_excerpt.

        """
        if len(self.excerpt.strip()):
            if self.html_mode == False:
                self.rendered_excerpt = render_markup(self.excerpt)
            else:
                self.rendered_excerpt = self.content
        else:
            self.rendered_excerpt = Truncator(self.rendered_content).words(
                    80,
                    html=True,
                    truncate=' ...'
            )
            self.excerpt = Truncator(self.content).words(
                    80,
                    html=True,
                    truncate=' ...'
            )
        return self.excerpt

    def meta_description(self):
        """
        If the meta-description is empty, create it from post.content.
        First render the markdown, strip any html tags, then truncate
        the text to 25 words.

        """

        if len(self.description.strip()) == 0:
            # remove extra html tags from the description
            d = strip_tags(render_markup(self.content))
            self.description = Truncator(d).words(
                    25,
                    html=True,
                    truncate=' ...'
            )
        return

    @models.permalink
    def get_absolute_url(self):
        return ('PostDetailView', (), {
                    'slug': self.slug,
                    'year': self.publish_date.strftime("%Y"),
                    })

    def get_next_post(self):
        """
        Returns the next active post.

        """
        if not self._next:
            # First we get a queryset of all Post objects excluding
            # the current Post. We then chop off any Posts that have
            # a publish_date earlier than current Post. Finally, the
            # queryset is sliced to leave only the previous post.
            try:
                queryset = Post.objects.active().exclude(id__exact=self.id)
                post = queryset.filter(
                    publish_date__gte=self.publish_date).order_by('publish_date')[0]
            except (Post.DoesNotExist, IndexError):
                post = None
            self._next = post

        return self._next

    def get_previous_post(self):
        """
        Returns the previous active post.

        """
        if not self._previous:
            try:
                queryset = Post.objects.active().exclude(id__exact=self.id)
                post = queryset.filter(
                    publish_date__lte=self.publish_date).order_by('-publish_date')[0]
            except (Post.DoesNotExist, IndexError):
                post = None
            self._previous = post

        return self._previous

    class Meta:
        ordering = ('-publish_date', 'title')
        get_latest_by = 'publish_date'



class Page(models.Model):
    """
    A model that stores data related to a single webpage.

    """
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    publish_date = models.DateTimeField(default=datetime.utcnow().replace(tzinfo=utc),
                                        help_text=('The date and time this \
                                            article will be published.'))
    content = models.TextField()
    head = models.TextField(blank=True, help_text="Will be place inside of \
                                                   the head tags.")
    foot = models.TextField(blank=True, help_text="Will be placed before the \
                                                   closing body tag.")
    rendered_content = models.TextField()

    description = models.TextField(blank=True,
                                   help_text="A brief explanation of the \
                                   page's content used by search engines. \
                                   (auto-magic)")
    slug = models.SlugField(unique_for_year='publish_date',
                            help_text='A URL-friendly representation of your \
                            posts title.')
    html_mode = models.BooleanField(default=False,
                                    help_text='Pages in html-mode will not be \
                                    rendered using Markdown.')
    draft_mode = models.BooleanField(default=False,
                                     help_text='Pages in draft-mode will not \
                                     appear to regular users.')
    author = models.ForeignKey(User, related_name="pages")

    # attach our custom manager
    objects = PostManager()

    def __init__(self, *args, **kwargs):
        super(Page, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Call required methods before saving.

        """
        self.render_content()
        self.meta_description()

        super(Page, self).save(*args, **kwargs)

    def render_content(self):
        """
        Use markdown2 to render post.rendered_content from post.content.

        """
        if self.html_mode == False:
            self.rendered_content = render_markup(self.content)
        else:
            self.rendered_content = self.content
        return self.rendered_content

    def meta_description(self):
        """
        If the meta-description is empty, create it from post.content.
        First render the markdown, strip any html tags, then truncate
        the text to 25 words.

        """

        if len(self.description.strip()) == 0:
            # remove extra html tags from the description
            d = strip_tags(render_markup(self.content))
            self.description = Truncator(d).words(
                    25,
                    html=True,
                    truncate=' ...'
            )
        return

    @models.permalink
    def get_absolute_url(self):
        return ('PageDetailView', (), {
                    'slug': self.slug,
                    })

    class Meta:
        ordering = ('-publish_date', 'title')
        get_latest_by = 'publish_date'
