from django.forms import  ModelForm
from .models import Room

class RoomForm(ModelForm):
    class Meta:
        model = Room
        # fields = ['host', 'name', 'description', 'topic']
        fields = '__all__'
        exclude = ['host', 'participants']
