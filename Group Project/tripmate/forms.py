from django import forms
from tripmate.models import UserProfile
from django.contrib.auth.models import User
from .models import Post, Comment
from django.contrib.auth.forms import UserCreationForm

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('website', 'picture')


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    gender = forms.ChoiceField(choices=UserProfile.GENDER_CHOICES, widget=forms.Select())
    picture = forms.ImageField(required=False)  

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'gender', 'picture']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['image', 'caption']

class CommentForm(forms.ModelForm):
    content = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'placeholder': 'Add a comment...',
            'rows': 3,
            'style': 'width: 100%; max-width: 500px;'
        })
    )
    class Meta:
        model = Comment
        fields = ['content']


class UserProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = UserProfile
        fields = ['gender', 'picture', 'bio']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(UserProfileForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['email'].initial = user.email

    def save(self, user=None):
        profile = super().save(commit=False)
        if user:
            user.email = self.cleaned_data['email']
            user.save()
        profile.save()
        return profile