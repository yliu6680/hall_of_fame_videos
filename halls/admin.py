from django.contrib import admin
from .models import Hall, Video

# Register your models here.
# these will make the admin page to see the models data
admin.site.register(Hall)
admin.site.register(Video)