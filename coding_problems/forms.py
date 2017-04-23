from django import forms
from .models import CodeSubmission

class CodeSubmissionForm(forms.ModelForm):
    class Meta:
        model = CodeSubmission
        fields = ('language', 'code',)
