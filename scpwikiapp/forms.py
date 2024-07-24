from django import forms
from .models import PDFDocument
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
    