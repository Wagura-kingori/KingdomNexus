from django import forms
from .models import Book, BookCategory, BorrowRecord


class BookCategoryForm(forms.ModelForm):
    class Meta:
        model = BookCategory
        fields = ['name']


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'category', 'isbn', 'copies_total']


class BorrowForm(forms.ModelForm):
    class Meta:
        model = BorrowRecord
        fields = ['student', 'book', 'due_date']
