from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import PasswordInput
from tinymce.widgets import TinyMCE
from ckeditor.widgets import CKEditorWidget

from .models import Task, Document
from ckeditor.fields import RichTextFormField

class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control form-group', 
        'placeholder': 'Name',
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control form-group', 
        'placeholder': 'Surname',
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control form-group', 
        'placeholder': 'Username',
    }))
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control form-group', 
        'placeholder': 'Email'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control form-group',
        'placeholder': 'password',
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control form-group',
        'placeholder': 'Confirm Password',
    }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

class TaskForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Task Title',
    }))

    completion_time = forms.DateTimeField(
        required=False,  # This makes the field optional
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local',
            'placeholder': 'YYYY-MM-DD HH:MM:SS',
        })
    )

    description = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))

    class Meta:
        model = Task
        fields = ['title', 'completion_time', 'description']

class DocumentForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Document Title',
    }))
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Document
        fields = ['title', 'content']

