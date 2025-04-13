from django.contrib import admin

from .models import User, InstructorProfile, Message, Review, Conversation, Instrument, InstructorCalendar, Booking

# Register your models here.
admin.site.register(User)
admin.site.register(InstructorProfile)
admin.site.register(Message)
admin.site.register(Review)
admin.site.register(Conversation)
admin.site.register(Instrument)
admin.site.register(InstructorCalendar)
admin.site.register(Booking)