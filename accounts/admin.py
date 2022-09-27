from django.contrib import admin
from .models import User, IntervieweeProfile, InterviewerProfile

admin.site.register(User)
admin.site.register(IntervieweeProfile)
admin.site.register(InterviewerProfile)