from .models import Post, Tag

def include_taglist(request):
    """Generates a list of tags to be added to every response."""
    tags = Tag.objects.all()
    return { 'tag_list': tags }
