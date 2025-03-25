from django.contrib import admin

from .models import User, InstructorProfile, Message, Review

# Register your models here.
admin.site.register(User)
admin.site.register(InstructorProfile)
admin.site.register(Message)
admin.site.register(Review)