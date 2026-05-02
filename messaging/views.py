from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Notice, Message
from .forms import NoticeForm, MessageForm

@login_required
def notices_list(request):
    notices = Notice.objects.all().order_by('-created_at')
    return render(request, 'messaging/notices_list.html', {'notices': notices})


@login_required
def notice_create(request):
    form = NoticeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        notice = form.save(commit=False)
        notice.created_by = request.user
        notice.save()
        return redirect('notices_list')
    return render(request, 'messaging/notice_form.html', {'form': form})


@login_required
def messages_list(request):
    messages = Message.objects.filter(receiver=request.user).order_by('-created_at')
    return render(request, 'messaging/messages_list.html', {'messages': messages})


@login_required
def send_message(request):
    form = MessageForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        msg = form.save(commit=False)
        msg.sender = request.user
        msg.save()
        return redirect('messages_list')
    return render(request, 'messaging/message_form.html', {'form': form})
