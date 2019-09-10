from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from .models import Hall, Video
# use the auth default login system forms
from django.contrib.auth.forms import UserCreationForm
# for auto login after signup successfully
from django.contrib.auth import authenticate, login
# form stuff
from .forms import VideoForm, SearchForm
# error pages, use to parse or plugin ajax json datatype
from django.http import Http404, JsonResponse
# show error messages
from django.forms.utils import ErrorList
# manipulate the url of youtube
import urllib
# 
import requests
# permission stuff for all webpages
from django.contrib.auth.decorators import login_required # use for the function based views
from django.contrib.auth.mixins import LoginRequiredMixin # use for the class based views

YOUTUBE_API_KEY = 'YOUTUBE_API_KEY'

# Create your views here.
def home(request):
	recent_halls = Hall.objects.all().order_by('-id')[:3]
	popular_halls = [Hall.objects.get(pk=3),Hall.objects.get(pk=4),Hall.objects.get(pk=5)]
	return render(request, "halls/home.html", {'recent_halls': recent_halls, "popular_halls": popular_halls})

@login_required
def dashboard(request):
	halls = Hall.objects.filter(user=request.user)
	return render(request, "halls/dashboard.html",{"halls": halls})

class SignUp(generic.CreateView):
	form_class = UserCreationForm
	success_url = reverse_lazy('home')
	template_name = 'registration/signup.html'
	# make the user auto login after signup successfully
	def form_valid(self, form):
		# super function use the method from its parent class, use to modify the method from the parent class
		# deatil, see here http://www.runoob.com/python/python-func-super.html
		view = super(SignUp, self).form_valid(form)
		username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
		user = authenticate(username=username, password=password)
		login(self.request, user)
		return view

# video stuff, all function based views, and use YouTube API
@login_required
def add_video(request, pk):
	# a form for user to add their urls
	form = VideoForm()
	# a form for user to search videos on YouTube
	search_form = SearchForm()
	# get the Hall id from the Hall object, the pk is the input for the add_video function
	hall = Hall.objects.get(pk=pk)

	if not hall.user == request.user:
		raise Http404

	if request.method == "POST":
		# CREATE
		# save the data from the post request, this step will record the user response to the form
		form = VideoForm(request.POST)
		# check the validation
		if form.is_valid():
			video = Video()
			video.hall = hall
			video.url = form.cleaned_data['url']
			# grap the youtube id, the get('v') is to get teh parameter 'v' inside the url
			parsed_url = urllib.parse.urlparse(video.url)
			video_id = urllib.parse.parse_qs(parsed_url.query).get('v')
			# make sure the user url is a valid youtube website url
			if video_id:
				video.youtube_id = video_id[0]
				# get the information from the url, the url are from the YouTube api youtube.videos.list api function
				response = requests.get(f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={ video_id[0] }&key={ YOUTUBE_API_KEY }')
				json = response.json()
				title = json['items'][0]['snippet']['title']
				video.title = title
				video.save()
				return redirect('detail_hall', pk)
			else:
				# add the error to the errorlist, and make the validation check for the url
				errors = form._errors.setdefault('url', ErrorList())
				errors.append('Need to be a valid YouTube URL')

	return render(request, 'halls/add_video.html', {'form': form, 'search_form': search_form, 'hall': hall})

# video_search for the ajax function
@login_required
def video_search(request):
	search_form = SearchForm(request.GET) # GET request from ajax
	if search_form.is_valid():
		# use urllib to get the search result from the search form
		encoded_term = urllib.parse.quote(search_form.cleaned_data['search_term'])
		response = requests.get(f'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=6&q={ encoded_term }&key={ YOUTUBE_API_KEY }')
		return JsonResponse(response.json())
	return JsonResponse({'error':'not validate form'})

class DeleteVideo(LoginRequiredMixin, generic.DeleteView):
	model = Video
	template_name = "halls/delete_video.html"
	success_url = reverse_lazy("dashboard")

	def get_object(self):
		video = super(DeleteVideo,self).get_object()
		if not video.hall.user == self.request.user:
			raise Http404
		return video

# CRUD create read update delete
class CreateHall(LoginRequiredMixin,generic.CreateView):
	model = Hall
	fields = ['title']
	template_name = "halls/create_hall.html"
	success_url = reverse_lazy("dashboard")

	def form_valid(self, form):
		form.instance.user = self.request.user
		super(CreateHall, self).form_valid(form)
		return redirect("dashboard")

class DetailHall(generic.DetailView):
	model = Hall
	template_name = "halls/detail_hall.html"

class UpdateHall(LoginRequiredMixin,generic.UpdateView):
	model = Hall
	fields = ['title']
	template_name = "halls/update_hall.html"
	success_url = reverse_lazy("dashboard")
	
	def get_object(self):
		hall = super(UpdateHall,self).get_object()
		if not hall.user == self.request.user:
			raise Http404
		return hall

class DeleteHall(LoginRequiredMixin,generic.DeleteView):
	model = Hall
	template_name = "halls/delete_hall.html"
	success_url = reverse_lazy("dashboard")

	def get_object(self):
		hall = super(DeleteHall,self).get_object()
		if not hall.user == self.request.user:
			raise Http404
		return hall

# def create_hall(request):
# 	if request.method == "POST":
# 		# get the form data
# 		# validate form data
# 		# create halls
# 		# save Hall
# 	else:
# 		# create a form for a hall
# 		# return the template

# video stuff, all function based views, and use YouTube API
	# if use form set, multiple same forms
	# use for the formset, for user submit multiple groups fo data
	# from django.forms import formset_factory
	# VideoFormSet=formset_factory(VideoForm, extra=5)
	# form = VideoFormSet()
	# filled_form = VideoFormSet(request.POST)
	#if filled_form.is_valid():
		# for form in filled_form:
			# other operations
	# in html file
	# {{ formset.management_form }}
	# {% for aform in form %}