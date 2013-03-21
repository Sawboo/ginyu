import re

from datetime import datetime
from django.db import models
from django.contrib.auth.models import User

from markdown import markdown
from django.template.defaultfilters import slugify
from django.utils.text import truncate_html_words


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
        """Replace spaces with dashes, in case someone adds such a tag manually"""

        name = name.replace(' ', '-').encode('ascii', 'ignore')
        name = TAG_RE.sub('', name)
        clean = name.lower().strip(", ")

        return clean

    def save(self, *args, **kwargs):
        """Cleans up any characters I don't want in a URL"""

        self.slug = Tag.clean_tag(self.name)
        super(Tag, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('articles_display_tag', (self.cleaned,))

    @property
    def cleaned(self):
        """Returns the clean version of the tag"""

        return self.slug or Tag.clean_tag(self.name)

    @property
    def rss_name(self):
        return self.cleaned

    class Meta:
        ordering = ('name',)



class ArticleManager(models.Manager):

    def active(self, user=None):
        """
        Retrieves all active articles that have past their publish_date
        """
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
        help_text=('The date and time this article will be published.'))
    draft_mode = models.BooleanField(default=False,
        help_text=('Posts in draft-mode will not appear to regular users.'))

    # html meta keywords and description
    keywords = models.CharField(max_length=250, blank=True,
        help_text=("A concise list of items and terms that describe the content of the post."))
    description = models.TextField(blank=True,
        help_text=("A brief explanation of the post's content used by search engines. (auto-magic)"))

    title = models.CharField(max_length=250)
    content = models.TextField(help_text=('A short teaser of your posts content.'))
    rendered_content = models.TextField()
    excerpt = models.TextField(blank=True,
        help_text=('A short teaser of your posts content.'))
    rendered_excerpt = models.TextField()
    tags = models.ManyToManyField(Tag, blank=True,
        help_text=('Tags that describe this article. Select from existing tags or create new tags. <br />'))
    slug = models.SlugField(unique_for_year='publish_date',
        help_text=('A URL-friendly representation of your posts title.'))
    author = models.ForeignKey(User, related_name="posts")

    objects = ArticleManager()

    def __init__(self, *args, **kwargs):
        """Makes sure that we have some rendered content to use"""

        super(Post, self).__init__(*args, **kwargs)

        self._next = None
        self._previous = None
        self._teaser = None

        if self.id:
            if not self.rendered_content or not len(self.rendered_content.strip()):
                self.save()

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Renders the article using the appropriate markup language."""

        self.render_markup()
        self.get_excerpt()
        self.meta_description()
        self.unique_slug()

        super(Post, self).save(*args, **kwargs)


    def render_markup(self):
        """converts markup from post.content to HTML"""

        original = self.rendered_content
        self.rendered_content = markdown(self.content)

        return (self.rendered_content != original)


    def get_excerpt(self):
        """if excerpt is blank, we create it from post.content"""

        if len(self.excerpt.strip()) == 0:
            original = self.content
            self.excerpt = truncate_html_words(self.content, 100)
            self.rendered_excerpt = markdown(self.excerpt)
            return (self.rendered_content != original)

        else:
            self.rendered_excerpt = markdown(self.excerpt)
            return (self.rendered_excerpt)


    def meta_description(self):
        """if meta description is empty, sets it to the article's excerpt"""

        if len(self.description.strip()) == 0:
            self.description = truncate_html_words(self.content, 25)
            return True

        return False


    def unique_slug(self):
        """
        Ensures that the slug is always unique for the year this article was
        posted
        """
        if not self.id:
            # make sure we have a slug first
            if not len(self.slug.strip()):
                self.slug = slugify(self.title)

            self.slug = self.get_unique_slug(self.slug)
            return True

        return False

    def get_unique_slug(self, slug):
        """Method to generate a unique slug"""

        # we need a publish date before we can do anything meaningful
        if type(self.publish_date) is not datetime:
            return slug

        orig_slug = slug
        year = self.publish_date.year
        counter = 1

        while True:
            not_unique = Post.objects.all()
            not_unique = not_unique.filter(publish_date__year=year, slug=slug)

            if len(not_unique) == 0:
                return slug

            slug = '%s-%s' % (orig_slug, counter)
            counter += 1

    @models.permalink
    def get_absolute_url(self):
        return ('articles_display_article', (self.publish_date.year, self.slug))

    class Meta:
        ordering = ('-publish_date', 'title')
        get_latest_by = 'publish_date'