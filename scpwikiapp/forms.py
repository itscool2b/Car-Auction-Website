from django import forms
from .models import PDFDocument, Chats
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    
class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'password')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
    
    class ChatForm(forms.ModelForm):
        
        class Meta:
            model = Chats
            fields = ['url', 'text']

    


