from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import PrivateMessage
from django.utils import timezone 
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.contrib.auth.models import User
from .models import PrivateMessage
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def chat_view(request, username):
    other_user = get_object_or_404(User, username=username)

    messages = PrivateMessage.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    ).order_by('timestamp')

    unread_messages = messages.filter(receiver=request.user, is_read=False)
    unread_messages.update(is_read=True, read_at=timezone.now())

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            PrivateMessage.objects.create(
                sender=request.user,
                receiver=other_user,
                content=content
            )
            return redirect('chat_view', username=other_user.username)

    return render(request, 'chat/chat_view.html', {
        'other_user': other_user,
        'messages': messages,
        'user': request.user,  

    })



@login_required
def chat_list(request):
    user = request.user

    chat_users = User.objects.filter(
        Q(sent_messages__receiver=user) | Q(received_messages__sender=user)
    ).distinct().exclude(id=user.id)

    chat_users = chat_users.annotate(
        unread_count=Count('sent_messages', filter=Q(sent_messages__receiver=user, sent_messages__is_read=False))
    )

    return render(request, 'chat/chat_list.html', {'chat_users': chat_users})

@login_required
def user_search(request):
    query = request.GET.get('q', '')
    users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)

    return render(request, 'chat/user_search.html', {'users': users, 'query': query})

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.contrib.auth.models import User

@login_required
def user_list(request):
    user = request.user

    chat_users = User.objects.exclude(id=user.id).annotate(
        unread_count=Count(
            'sent_messages',
            filter=Q(sent_messages__receiver=user, sent_messages__is_read=False)
        )
    )

    return render(request, 'chat/user_list.html', {'chat_users': chat_users})


from django.http import JsonResponse

@login_required
def fetch_messages(request, username):
    other_user = get_object_or_404(User, username=username)

    messages = PrivateMessage.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    ).order_by('timestamp')

    data = []
    for msg in messages:
        data.append({
            'sender': msg.sender.username,
            'receiver': msg.receiver.username,
            'content': msg.content,
            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'is_self': msg.sender == request.user
        })

    return JsonResponse(data, safe=False)
