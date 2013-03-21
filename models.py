from datetime import datetime
from django.db import models
from django.contrib.auth.models import User

from markdown import markdown
from django.template.defaultfilters import slugify
from django.utils.text import truncate_html_words

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
    keywords = models.TextField(blank=True,
        help_text=("If omitted, the keywords will be the same as the article tags."))
    description = models.TextField(blank=True,
        help_text=("If omitted, the description will be determined by the first bit of the article's content."))

    title = models.CharField(max_length=250)
    content = models.TextField()
    rendered_content = models.TextField()
    excerpt = models.TextField(blank=True)
    rendered_excerpt = models.TextField()
    slug = models.SlugField(unique_for_year='publish_date')
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

        # do some things that require an ID first
        # requires_save = self.do_auto_tag(using)
        # requires_save |= self.do_tags_to_keywords()
        # requires_save |= self.do_default_site(using)

        # if requires_save:
            # bypass the other processing
            # super(Post, self).save()



    def render_markup(self):
        """Turns markup into HTML"""

        original = self.rendered_content
        self.rendered_content = markdown(self.content)

        return (self.rendered_content != original)


    def meta_description(self):
        """
        If meta description is empty, sets it to the article's excerpt.

        Returns True if an additional save is required, False otherwise.
        """

        if len(self.description.strip()) == 0:
            self.description = truncate_html_words(self.content, 25)
            return True

        return False

    def get_excerpt(self):
        """
        Retrieve some part of the article's description.
        """
        if len(self.excerpt.strip()) == 0:
            original = self.content
            self.excerpt = truncate_html_words(self.content, 100)
            self.rendered_excerpt = markdown(self.excerpt)
            return (self.rendered_content != original)

        else:
            self.rendered_excerpt = markdown(self.excerpt)
            return (self.rendered_excerpt)


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