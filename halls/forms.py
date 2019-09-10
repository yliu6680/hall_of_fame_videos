from .models import Video
from django import forms

# pass a created model inside the models.py to the django server, and the django will automatically generate a form for this particular model
class VideoForm(forms.ModelForm):
	# store the information or meta data of the model
	class Meta():
		model = Video
		# select the fields that we want in the model, the char should correspond to the name in the model class 
		# other unselected fields will not be shown
		fields = ['url']
		labels = {'url':"YouTube Url"}

class SearchForm(forms.Form):
	search_term = forms.CharField(max_length=255, label='Search for Videos')
