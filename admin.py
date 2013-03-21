from django.contrib import admin
from django.contrib.auth.models import User
from forms import PostAdminForm
from models import Post

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
                        'publish_date',
                        'slug',
                        'draft_mode')
        }),
        ('Metadata', {
            'fields': ('keywords', 'description',),
            'classes': ('collapse',)
        }),
    )

    prepopulated_fields = {'slug': ('title',)}

    class Media:
        """Load custom css into the admin site"""
        css = { 'all': ('/static/epiceditor/style.css',) }

    def save_model(self, request, obj, form, change):
        """Set the post's author based on the logged in user"""
        obj.author = request.user
        obj.save()

admin.site.register(Post, PostAdmin)
