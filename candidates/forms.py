from django.contrib.auth.models import User
from .models import Candidate
from django import forms


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ('phone', 'resume', 'resume_url', 'website')
