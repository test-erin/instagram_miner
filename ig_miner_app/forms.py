from django import forms
from .models import Campaign

class PostForm(forms.ModelForm):

    class Meta:
        model = Campaign
        fields = ('Campaign_Title', 'Start_Date', 'End_Date', 'Hashtag')