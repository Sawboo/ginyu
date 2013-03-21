from django import forms
from models import Post
from widgets import AdminEpicEditorWidget

class PostAdminForm(forms.ModelForm):

    content=forms.CharField(widget=AdminEpicEditorWidget())
    excerpt=forms.CharField(widget=AdminEpicEditorWidget())

    class Meta:
        model = Post



