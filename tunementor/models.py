from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    """User Model for both Instructors and Apprentices"""
    ROLE_CHOICES = [
        ('instructor', 'Instructor'),
        ('apprentice', 'Apprentice')
    ] 
    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default="apprentice")

    def is_instructor(self):
        return self.role == "instructor"
    
    def is_apprentice(self):
        return self.role == "apprentice"
    
    def __str__(self):
        return f"Username: {self.username} | Email: {self.email}"
    

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


class Message(models.Model):
    """Message Model"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    message = models.CharField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sender: {self.sender.username} | Receiver: {self.receiver.username} | Message: {self.message[:20]}/"
