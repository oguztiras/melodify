from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import InstructorProfile, Review, Message
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

        # Create messages
        self.message = Message.objects.create(sender=self.apprentice1, receiver=self.instructor, message="Hello Teacher!")

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

    def test_message_creation(self):
        """Check Message Creation"""
        self.assertEqual(self.message.sender.username, "appr1")
        self.assertEqual(self.message.receiver.username, "inst1")
        self.assertEqual(self.message.message, "Hello Teacher!")

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

    def test_send_msg(self):
        c = Client()
        c.login(username="appr1", password="pass")

        url = reverse("send_msg")
        data = {
            "receiver": self.instructor.id,
            "message": "This is a test message!"
        }
        response = c.post(url, json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Message sent succuesfully!")
    
    def test_search(self):
        """Check Search"""
        url = reverse("search")
        c = Client()
        response = c.get(url, {
            "city": "hamburg",
            "level": "beginner"
        })

        self.assertEqual(response.status_code, 200)

    def test_post_review(self):
        """Chech Review Posting"""
        c = Client()
        c.login(username="appr1", password="pass")

        url = reverse("review")
        data = {
            "instructorProfileId": self.profile.id,
            "rating": 5,
            "comment": "This teacher is great!"
        }

        response = c.post(url, json.dumps(data), content_type="application/json")
        response_data = response.json()

        self.assertEqual(response_data["message"], "Reviewed succesfully")
        self.assertEqual(response_data["reviewer"], self.apprentice1.username)
        self.assertEqual(response_data["comment"], "This teacher is great!")
        self.assertEqual(response_data["rating"], 5)
        self.assertIsNotNone(response_data["avrRating"])
        self.assertIsNotNone(response_data["reviewId"])

    def test_edit_review(self):
        c = Client()
        c.login(username="appr1", password="pass")

        url = reverse("editReview")
        data = {
            "reviewId": self.review1.id,
            "editedComment": "This comment is edited!",
            "editedRating": 4
        }

        response = c.put(url, json.dumps(data), content_type="application/json")
        response_data = response.json()

        self.assertEqual(response_data["message"], "Review updated succesfully")

    def test_edit_reveiw_wrong_reqest(self):
        """Test Wrong(post) Request"""
        c = Client()
        c.login(username="appr1", password="pass")

        url = reverse("editReview")
        data = {
            "reviewId": self.review1.id,
            "editedComment": "This comment is edited!",
            "editedRating": 4
        }

        response = c.post(url, json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, 405)

    def test_messages(self):
        """Check Getting Messages"""
        c = Client()
        c.login(username="inst1", password="pass")

        url = reverse("message", args=[self.instructor.id])
        response = c.get(url)

        self.assertEqual(response.status_code, 200)

    def test_detele_msg(self):
        """Check Message Deleting"""
        c = Client()
        c.login(username="inst1", password="pass")

        url = reverse("delete_msg")
        data = {
            "messageId": self.message.id
        }

        response = c.post(url, json.dumps(data), content_type="application/json")

        self.assertEqual(response.json()["message"], "Message deleted succuesfully!")

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