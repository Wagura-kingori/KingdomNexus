from django import forms
from .models import AssetCategory, Asset, AssetIssue

class AssetCategoryForm(forms.ModelForm):
    class Meta:
        model = AssetCategory
        fields = "__all__"


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = "__all__"


class AssetIssueForm(forms.ModelForm):
    class Meta:
        model = AssetIssue
        fields = "__all__"
