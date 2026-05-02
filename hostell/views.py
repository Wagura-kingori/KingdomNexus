from django.shortcuts import render, redirect, get_object_or_404
from .models import Hostel, HostelRoom, Boarder
from .forms import HostelForm, HostelRoomForm, BoarderForm


def hostel_list(request):
    hostels = Hostel.objects.all()
    return render(request, "hostel/hostel_list.html", {"hostels": hostels})


def hostel_form(request, pk=None):
    item = get_object_or_404(Hostel, pk=pk) if pk else None
    form = HostelForm(request.POST or None, instance=item)
    if form.is_valid():
        form.save()
        return redirect("hostel_list")
    return render(request, "hostel/hostel_form.html", {"form": form})


def room_list(request):
    rooms = HostelRoom.objects.select_related("hostel").all()
    return render(request, "hostel/room_list.html", {"rooms": rooms})


def room_form(request, pk=None):
    room = get_object_or_404(HostelRoom, pk=pk) if pk else None
    form = HostelRoomForm(request.POST or None, instance=room)
    if form.is_valid():
        form.save()
        return redirect("room_list")
    return render(request, "hostel/room_form.html", {"form": form})


def boarder_list(request):
    boarders = Boarder.objects.select_related("room", "student").all()
    return render(request, "hostel/boarder_list.html", {"boarders": boarders})


def boarder_form(request, pk=None):
    boarder = get_object_or_404(Boarder, pk=pk) if pk else None
    form = BoarderForm(request.POST or None, instance=boarder)
    if form.is_valid():
        new_boarder = form.save()
        return redirect("boarder_list")
    return render(request, "hostel/boarder_form.html", {"form": form})
