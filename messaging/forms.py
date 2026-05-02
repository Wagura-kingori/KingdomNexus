from django import forms
from .models import Notice, Message

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'message', 'notice_type', 'target_class', 'target_student']


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['receiver', 'subject', 'body']
