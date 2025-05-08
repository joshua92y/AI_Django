# gbook/forms.py
from django import forms
from .models import GuestBookEntry

class GuestBookEntryForm(forms.ModelForm):
    class Meta:
        model = GuestBookEntry
        fields = ['title', 'message']  # ✅ file 추가
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '제목을 입력하세요'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '내용을 입력하세요',
                'rows': 4
            }),
        }
