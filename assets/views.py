from django.shortcuts import render, redirect, get_object_or_404
from .models import AssetCategory, Asset, AssetIssue
from .forms import AssetCategoryForm, AssetForm, AssetIssueForm

def category_list(request):
    categories = AssetCategory.objects.all()
    return render(request, "assets/category_list.html", {"categories": categories})


def category_form(request, pk=None):
    instance = get_object_or_404(AssetCategory, pk=pk) if pk else None
    form = AssetCategoryForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect("category_list")
    return render(request, "assets/category_form.html", {"form": form})


def asset_list(request):
    assets = Asset.objects.all()
    return render(request, "assets/asset_list.html", {"assets": assets})


def asset_form(request, pk=None):
    instance = get_object_or_404(Asset, pk=pk) if pk else None
    form = AssetForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect("asset_list")
    return render(request, "assets/asset_form.html", {"form": form})


def issue_list(request):
    issues = AssetIssue.objects.all()
    return render(request, "assets/issue_list.html", {"issues": issues})


def issue_form(request, pk=None):
    instance = get_object_or_404(AssetIssue, pk=pk) if pk else None
    form = AssetIssueForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect("issue_list")
    return render(request, "assets/issue_form.html", {"form": form})
