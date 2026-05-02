from django import forms
from .models import Hostel, HostelRoom, Boarder


class HostelForm(forms.ModelForm):
    class Meta:
        model = Hostel
        fields = "__all__"


class HostelRoomForm(forms.ModelForm):
    class Meta:
        model = HostelRoom
        fields = "__all__"


class BoarderForm(forms.ModelForm):
    class Meta:
        model = Boarder
        fields = "__all__"
