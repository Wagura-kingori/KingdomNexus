from django.urls import path
from . import views
app_name = "assets" 

urlpatterns = [
    path("categories/", views.category_list, name="category_list"),
    path("categories/add/", views.category_form, name="category_create"),
    path("categories/<int:pk>/edit/", views.category_form, name="category_edit"),

    path("assets/", views.asset_list, name="asset_list"),
    path("assets/add/", views.asset_form, name="asset_create"),
    path("assets/<int:pk>/edit/", views.asset_form, name="asset_edit"),

    path("issues/", views.issue_list, name="issue_list"),
    path("issues/add/", views.issue_form, name="issue_create"),
    path("issues/<int:pk>/edit/", views.issue_form, name="issue_edit"),
]
