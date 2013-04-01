from django import forms
from models import Post
from widgets import AdminEpicEditorWidget


class PostAdminForm(forms.ModelForm):

    # content = forms.CharField(widget=AdminEpicEditorWidget(),
    #                           help_text=('Posts will be rendered using <a \
    #                           href="http://daringfireball.net/projects/\
    #                           markdown/syntax">markdown</a>. You can preview \
    #                           the output with the icons in the editor.'))
    # excerpt=forms.CharField(widget=AdminEpicEditorWidget(),
    #     help_text=('A short teaser of your posts content.'))

    class Meta:
        model = Post
