from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import modelformset_factory
from .models import Profile, Post, PostMedia, Comment, PDFDocument

# --- User Registration Form ---
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


# --- User Update Form ---
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
        }


# --- Profile Update Form ---
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'photo']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


# --- User Profile Form with Followers ---
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'photo', 'followers']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'followers': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


# --- Post Form ---
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['category', 'title', 'content', 'youtube_url', 'image', 'video', 'status', 'is_pinned']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'youtube_url': forms.URLInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'video': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


# --- PostMedia Form ---
class PostMediaForm(forms.ModelForm):
    class Meta:
        model = PostMedia
        fields = ['image', 'video']


# --- FormSet for PostMedia ---
PostMediaFormSet = modelformset_factory(PostMedia, form=PostMediaForm, extra=3, can_delete=False)


# --- Comment Form ---
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Write your comment...',
                'class': 'form-control'
            }),
        }


# --- PDF Upload Form ---
class PDFUploadForm(forms.ModelForm):
    class Meta:
        model = PDFDocument
        fields = ['title', 'description', 'file', 'category']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }
