from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, BookCategory, BorrowRecord
from .forms import BookForm, BookCategoryForm, BorrowForm


def categories_list(request):
    categories = BookCategory.objects.all()
    return render(request, "library/categories_list.html", {"categories": categories})


def category_form(request, pk=None):
    category = BookCategory.objects.get(pk=pk) if pk else None
    form = BookCategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        return redirect("library:categories")
    return render(request, "library/category_form.html", {"form": form})


def books_list(request):
    books = Book.objects.all()
    return render(request, "library/books_list.html", {"books": books})


def book_form(request, pk=None):
    book = Book.objects.get(pk=pk) if pk else None
    form = BookForm(request.POST or None, instance=book)
    if form.is_valid():
        form.save()
        return redirect("library:books")
    return render(request, "library/book_form.html", {"form": form})


def borrow_list(request):
    borrows = BorrowRecord.objects.all()
    return render(request, "library/borrow_list.html", {"borrows": borrows})


def borrow_form(request):
    form = BorrowForm(request.POST or None)
    if form.is_valid():
        borrow = form.save()

        # Updat available copies
        borrow.book.copies_available -= 1
        borrow.book.save()

        return redirect("library:borrow_list")

    return render(request, "library/borrow_form.html", {"form": form})


def return_book(request, pk):
    borrow = get_object_or_404(BorrowRecord, pk=pk)
    borrow.date_returned = timezone.now().date()
    borrow.save()

    borrow.book.copies_available += 1
    borrow.book.save()

    return redirect("library:borrow_list")
