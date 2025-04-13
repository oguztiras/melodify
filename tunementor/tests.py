from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import InstructorProfile, Review, Message, Conversation
from django.urls import reverse
import json

User = get_user_model()

# Create your tests here.
class TuneMentorTestCase(TestCase):

    def setUp(self):

        # Create Users (instructor and apprentice)
        self.instructor = User.objects.create_user(username="inst1", password="pass", role="instructor")
        self.instructor2 = User.objects.create_user(username="inst2", password="pass", role="instructor")
        self.apprentice1 = User.objects.create_user(username="appr1", password="pass", role="apprentice")
        self.apprentice2 = User.objects.create_user(username="appr2", password="pass", role="apprentice")

        # Create profiles
        self.profile = InstructorProfile.objects.create(instructor=self.instructor, bio="Experienced Teacher!")
        self.profile2 = InstructorProfile.objects.create(instructor=self.instructor2, city="hamburg", level="beginner")

        # Create reviews
        self.review1 = Review.objects.create(reviewer=self.apprentice1, instructor_profile=self.profile, rating=5, comment="Great Teacher!")
        self.review2 = Review.objects.create(reviewer=self.apprentice2, instructor_profile=self.profile, rating=4, comment="Good Teacher!")

        # Create conversation
        self.conversation = Conversation.objects.create()
        self.conversation.participants.set([self.apprentice1, self.instructor])

        # Create messages
        self.message = Message.objects.create(conversation=self.conversation, sender=self.apprentice1, message="Hello Teacher!")

    def test_user_creation(self):
        """Check User Creation for Instructor and Apprentice"""
        self.assertEqual(self.instructor.role, "instructor")
        self.assertEqual(self.apprentice1.role, "apprentice")

    def test_instructor_profile_creation(self):
        """Check Instructor Profile Creation"""
        self.assertEqual(self.profile.instructor.username, "inst1")
        self.assertEqual(self.profile.bio, "Experienced Teacher!")

    def test_get_reviews(self):
        """Check Reviews Count"""
        self.assertEqual(self.profile.get_reviews().count(), 2)

    def test_avr_rating(self):
        """Check Average Rating"""
        self.assertEqual(self.profile.get_avr_rating(), 4.5)

    def test_review_serialization(self):
        """Check Review Serialization"""
        serialized_review = self.review1.serialize()
        self.assertEqual(serialized_review["reviewer"], "appr1")
        self.assertEqual(serialized_review["instructor"], "inst1")
        self.assertEqual(serialized_review["rating"], 5)
        self.assertEqual(serialized_review["comment"], "Great Teacher!")

    def test_index(self):
        """Check Index Request"""
        c = Client()
        response = c.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["profiles"].count(), 2)

    def test_client(self):
        """Check Client Request"""
        client_id = self.profile.id

        c = Client()
        c.login(username="appr1", password="pass")
        response = c.get(reverse("client", args=[client_id]))

        self.assertEqual(response.status_code, 200)
    
    def test_search(self):
        """Check Search"""
        url = reverse("search")
        c = Client()
        response = c.get(url, {
            "city": "hamburg",
            "level": "beginner"
        })

        self.assertEqual(response.status_code, 200)

    def test_change_password(self):
        """Check Password Changing"""
        c = Client()
        c.login(username="inst1", password="pass")

        url = reverse("change_pass", args=[self.instructor.id])
        response = c.post(url, {
            "password": "pass",
            "password_new": "newpass123",
            "confirmation": "newpass123"
        })

        self.assertEqual(response.status_code, 200)

        c.logout()
        login_success = self.client.login(username="inst1", password="newpass123")
        self.assertTrue(login_success)