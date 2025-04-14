from django import forms
from django.contrib.auth.models import User
from .models import Post, Comment


class ProfileChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']


class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title',
            'text',
            'pub_date',
            'location',
            'category',
            'image'
        ]
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }


class CommentsForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
