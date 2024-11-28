from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.db.models import CASCADE, SET_NULL


class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)  #true allows to be empty
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    #auto_now - date stamp of modified or changed
    updated = models.DateTimeField(auto_now=True)
    #auto_now_add - date stamp of creation
    created = models.DateTimeField(auto_now_add=True)


    class Meta:
        # how to sort data in this case the newest will be first
        ordering =  ['-updated', '-created']

    def __str__(self):
        return self.name


class Message(models.Model):
    #Django already has a user model
    user = models.ForeignKey(User, on_delete=CASCADE)
    #Cascade = when you delete Room it will delete all children components of the room
    #another option is SET_NULL will set children to Null when delete room
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        # how to sort data in this case the newest will be first
        ordering =  ['-updated', '-created']

    def __str__(self):
        return self.body[0:50]
