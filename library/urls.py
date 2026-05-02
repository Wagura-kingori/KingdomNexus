from django.urls import path
from . import views

app_name = "library"

urlpatterns = [
    path("categories/", views.categories_list, name="categories"),
    path("categories/add/", views.category_form, name="category_add"),
    path("categories/<int:pk>/edit/", views.category_form, name="category_edit"),

    path("books/", views.books_list, name="books"),
    path("books/add/", views.book_form, name="book_add"),
    path("books/<int:pk>/edit/", views.book_form, name="book_edit"),

    path("borrow/", views.borrow_list, name="borrow_list"),
    path("borrow/add/", views.borrow_form, name="borrow_add"),
    path("borrow/<int:pk>/return/", views.return_book, name="return_book"),
]
