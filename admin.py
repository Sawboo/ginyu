from django.contrib import admin
from django.contrib.auth.models import User
from forms import PostAdminForm
from models import Tag, Post


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'post_count')

    prepopulated_fields = {'slug': ('name',)}

    def post_count(self, obj):
        return obj.post_set.count()
    post_count.short_description=('# of posts tagged')


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'publish_date', 'draft_mode')
    list_editable = ['draft_mode']
    list_filter = ('author', 'draft_mode', 'publish_date')
    list_per_page = 25
    search_fields = ('title', 'description', 'content')
    date_hierarchy = 'publish_date'
    form = PostAdminForm
    inlines = []

    fieldsets = (
        (None, {'fields': (
                        'title',
                        'excerpt',
                        'content',
                        'tags',
                        'publish_date',
                        'slug',
                        'draft_mode')
        }),
        ('Metadata', {
            'fields': ('keywords', 'description',),
            'classes': ('collapse',)
        }),
    )

    filter_horizontal = ('tags',)
    prepopulated_fields = {'slug': ('title',)}

    def tag_count(self, obj):
        return str(obj.tags.count())
    tag_count.short_description = ('Tags')

    class Media:
        """Load custom css into the admin site"""
        css = { 'all': ('/static/epiceditor/style.css',) }

    def save_model(self, request, obj, form, change):
        """Set the post's author based on the logged in user"""
        obj.author = request.user
        obj.save()

admin.site.register(Tag, TagAdmin)
admin.site.register(Post, PostAdmin)
