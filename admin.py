from django.contrib import admin
from .models import Tag, Post


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'post_count')
    prepopulated_fields = {'slug': ('name',)}

    def post_count(self, obj):
        """counts the number of post-relationships for each tag"""
        return obj.post_set.count()
    post_count.short_description = '# of posts tagged'


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'publish_date', 'draft_mode')
    list_editable = ['draft_mode']
    list_filter = ('author', 'draft_mode', 'publish_date')
    list_per_page = 25
    search_fields = ('title', 'description', 'content')
    date_hierarchy = 'publish_date'
    inlines = []

    fieldsets = (
        (None, {'fields': (
                'title',
                'content',
                'tags',
                'publish_date',
                'draft_mode')
                }),
        ('Metadata', {
            'fields': ('slug', 'excerpt', 'description',),
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
        css = {'all': ('/static/admin-style.css',)}

    def save_model(self, request, obj, form, change):
        """Set the post's author based on the logged in user"""
        obj.author = request.user
        obj.save()

admin.site.register(Tag, TagAdmin)
admin.site.register(Post, PostAdmin)
