
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Message
from .forms import MessageForm
from django.contrib.auth.models import User

@login_required
def inbox(request):
    messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')
    return render(request, 'messaging/inbox.html', {'messages': messages})

@login_required
def sent_messages(request):
    messages = Message.objects.filter(sender=request.user).order_by('-timestamp')
    return render(request, 'messaging/sent.html', {'message': sent_messages})

@login_required
def send_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            return redirect('messaging:inbox')
    else:
        form = MessageForm()
    return render(request, 'messaging/send_message.html', {'form': form})

@login_required
def message_detail(request, pk):
    message = get_object_or_404(Message, pk=pk)
    if message.recipient == request.user:
        message.is_read = True
        message.save()
    return render(request, 'messaging/message_detail.html', {'message': message})


@login_required
def reply_message(request, pk):
    original = get_object_or_404(Message, pk=pk)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.sender = request.user
            reply.recipient = original.sender
            reply.subject = "Re: " + original.subject if not original.subject.startswith("Re:") else original.subject
            reply.save()
            return redirect('messaging:inbox')
    else:
        # pre-fill subject
        form = MessageForm(initial={'subject': "Re: " + original.subject})

    return render(request, 'messaging/reply_message.html', {'form': form, 'original': original})

