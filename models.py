# The markdown2 python package is required
import markdown2

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import truncate_words, truncate_html_words
from datetime import datetime


def render_markup(markdown):
    """
    Uses markdown2 to return html markup.

    Extra implementations include:
    * fenced-code-blocks with syntax highlighting.
    * http://github.com/trentm/python-markdown2/wiki/fenced-code-blocks
    * wiki-tables support.
    * http://github.com/trentm/python-markdown2/wiki/wiki-tables

    """
    markup = markdown2.markdown(markdown, extras=[
        "fenced-code-blocks",
        "wiki-tables",
        "code-friendly"])
    return markup


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
        now = datetime.now()
        return self.get_query_set().filter(
            publish_date__lte=now, draft_mode=False)


class Post(models.Model):
    """
    A model that stores data related to a single blog post.

    """
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    publish_date = models.DateTimeField(default=datetime.now,
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
        self.rendered_content = render_markup(self.content)
        return self.rendered_content

    def render_excerpt(self):
        """
        If self.excerpt is blank generate it from `self.content`.
        Otherwise, render self.excerpt via markdown.

        """
        if len(self.excerpt.strip()):
            self.rendered_excerpt = render_markup(self.excerpt)
        else:
            self.rendered_excerpt = truncate_html_words(
                self.rendered_content, 80)
            self.excerpt = truncate_html_words(self.content, 80)
        return self.excerpt

    def meta_description(self):
        """
        If the meta-description is empty, create it from post.content.

        """
        if len(self.description.strip()) == 0:
            self.description = truncate_words(self.content, 25)
        return self.description

    @models.permalink
    def get_absolute_url(self):
        return ('PostDetailView', (), {
                'slug': self.slug, })

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
