from django.db import models
from django.contrib.auth.models import AbstractUser
from schedule.models import Calendar
from django.conf import settings
from schedule.models import Event

class InstructorCalendar(Calendar):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="calendars"
    )

    def __str__(self):
        return f"{self.owner.username}'s Calendar: {self.name}"

# Create your models here.
class User(AbstractUser):
    """User Model for both Instructors and Apprentices"""
    ROLE_CHOICES = [
        ('instructor', 'Instructor'),
        ('apprentice', 'Apprentice')
    ] 
    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default="apprentice")
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def is_instructor(self):
        return self.role == "instructor"
    
    def is_apprentice(self):
        return self.role == "apprentice"
    
    def __str__(self):
        return f"Username: {self.username} | Email: {self.email}"
    

class Instrument(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
# django shell: (python manage.py shell)
# from tunementor.models import Instrument
# for name in ["Guitar", "Piano", "Violin", "Drums", "Flute", "Bass"]:
#     Instrument.objects.get_or_create(name=name)
# exit()

class InstructorProfile(models.Model):
    """Instructor Profile Model"""
    CITY_CHOICES = [
        ('berlin', 'Berlin'),
        ('munich', 'Munich'),
        ('hamburg', 'Hamburg')
    ]

    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate')
    ]

    instructor = models.OneToOneField(User, on_delete=models.CASCADE, related_name="instructor_profile")
    bio = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=32, choices=CITY_CHOICES, default="berlin")
    level = models.CharField(max_length=32, choices=LEVEL_CHOICES, default="intermediate")
    instruments = models.ManyToManyField(Instrument, blank=True, related_name="instructors")

    def __str__(self):
        return f"Username: {self.instructor.username} | Email: {self.instructor.email} | City: {self.city}"
    
    def get_reviews(self):
        return self.reviews.all().order_by('-id')
    
    def get_avr_rating(self):
        reviews = self.get_reviews()
        if reviews.exists():
            return sum(review.rating for review in reviews) / reviews.count()
        return None
    
    def serialize(self):
        return {
            "id": self.id,
            "username": self.instructor.username,
            "email": self.instructor.email,
            "city": self.city,
            "level": self.level,
            "bio": self.bio,
            "reviews": [review.serialize() for review in self.get_reviews()],
            "average_rating": self.get_avr_rating()
        }
    

class Review(models.Model):
    """Review Model"""
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews_written")
    instructor_profile = models.ForeignKey(InstructorProfile, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reviewer: {self.reviewer.username} | Instructor: {self.instructor_profile.instructor.username} | Rating: {self.rating}"
    
    def serialize(self):
        return {
            "id": self.id,
            "reviewer": self.reviewer.username,
            "instructor": self.instructor_profile.instructor.username,
            "rating": self.rating,
            "comment": self.comment,
            "timestamp": self.timestamp
        }


class Conversation(models.Model):
    """Conversation Model"""
    participants = models.ManyToManyField(User, related_name="conversations")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        participants = ", ".join([user.username for user in self.participants.all()])
        return f"Conversation between {participants}"
    
    def get_other_participant(self, user):
        return self.participants.exclude(id=user.id).first()


class Message(models.Model):
    """Message Model"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username}: {self.message[:20]}"


class Booking(models.Model):
    STATE_CHOICES = [
        ('scheduled', 'Scheduled'), 
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'), 
    ]

    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        related_name="booking"
    )
    apprentice = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    state = models.CharField(max_length=16, choices=STATE_CHOICES, default='scheduled')
    cancellation_reason = models.TextField(blank=True, null=True)
    booked_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Booking for '{self.event.title}' by {self.apprentice.username} [{self.state}]"