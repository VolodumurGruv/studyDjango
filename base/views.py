from pydoc_data.topics import topics
from sqlite3 import connect

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
# Create your views here.
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm


def home(req):
    return render(req, 'base/home.html')


def login_page(req):
    page = 'login'
    if req.user.is_authenticated:
        return redirect('/home')

    if req.method == "POST":
        username = req.POST.get('username').lower().strip()
        password = req.POST.get('password')


        try:
            user = User.objects.get(username=username)
        except Exception as err:
            messages.error(req, err)

        user = authenticate(req, username=username, password=password)

        if user is not None:
            login(req, user)
            return redirect('home')
        else:
            messages.error(req, "Username or password doesn't exist")

    context = {'page': page}
    return render(req, 'base/login_register.html', context)


def logout_user(req):
    logout(req)
    return redirect('home')


def register_page(req):
    page = 'register'
    form = UserCreationForm()

    if req.method == "POST":
        form = UserCreationForm(req.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower().strip()
            user.save()
            login(req, user)
            return redirect('home')
        else:
            messages.error(req, "An error occurred during registration")

    context = {"page": page, "form": form}
    return  render(req, 'base/login_register.html', context)


def room(req):
    # search
    q = req.GET.get('q') if req.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    room_count = rooms.count()
    topics = Topic.objects.all()
    # filter recent activities by matching browsing topics
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {
        'rooms': rooms,
        'topics': topics,
        "room_count": room_count,
        "room_messages": room_messages,
    }
    return render(req, 'base/room.html', context)


def user_profile(req, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {
        'user': user,
        'rooms': rooms,
        'room_messages': room_messages,
        'topics': topics,
    }
    return render(req, 'base/profile.html', context)

def room_id(req, pk):
    room = Room.objects.get(id=pk)
    room_msg = room.message_set.all()
    participants = room.participants.all()

    if req.method == "POST":
        msg = Message.objects.create(
            user = req.user,
            room = room,
            body = req.POST.get('body_msg')
        )
        room.participants.add(req.user)
        return redirect(f'/room/{room.id}') #it works
        # return redirect('room', pk=room.id) doesn't work

    context = {'room': room, 'room_msg': room_msg, 'participants': participants}
    return render(req, 'base/room_item.html', context)


@login_required(login_url='/login')
def create_room(req):
    form = RoomForm()

    if req.method == "POST":
        form = RoomForm(req.POST)

        if form.is_valid():
            room = form.save(commit=False)
            room.host = req.user
            room.save()
            return redirect('home')

    context = {'form': form}
    return render(req, 'base/room_form.html', context)


def update_room(req, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if req.user != room.host:
        return HttpResponse('You are not allowed here!!!')

    if req.method == 'POST':
        form = RoomForm(req.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('room')

    context = {'form': form}
    return render(req, 'base/room_form.html', context)


@login_required(login_url='/login')
def delete_room(req, pk):
    room = Room.objects.get(id=pk)
    if req.method == "POST":
        room.delete()
        return redirect('home')
    return render(req, 'base/delete.html', {'obj': room})

@login_required(login_url='/login')
def delete_message(req, pk):
    message = Message.objects.get(id=pk)

    if req.user != message.user:
        return HttpResponse("You don't have permission!")
    if req.method == "POST":
        message.delete()
        return redirect('room')
    return render(req, 'base/delete.html', {'obj': message})
