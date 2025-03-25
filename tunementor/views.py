from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.urls import reverse
from django.db import IntegrityError
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import User, InstructorProfile, Message, Review

# Create your views here.
def index(request):
    profiles = InstructorProfile.objects.all().order_by('?')

    return render(request, "tunementor/index.html", {
        "profiles": profiles
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "tunementor/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "tunementor/login.html")
    

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        role = request.POST["role"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "tunementor/register.html", {
                "message": "Passwords must match."
            })
        
        # Ensure role matches model's role feature
        valid_roles = [choice[0] for choice in User.ROLE_CHOICES]
        if role not in valid_roles:
            return render(request, "tunementor/register.html", {
                "message": "Role must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password, role=role)
            user.save()
        except IntegrityError:
            return render(request, "tunementor/register.html", {
                "message": "Username already taken."
            })
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "tunementor/register.html")
    

@login_required(login_url='login')
def client(request, id):
    profile = InstructorProfile.objects.get(id=id)
    reviews = profile.get_reviews()
    avr_rating = profile.get_avr_rating()
    reviewers = [review.reviewer.username for review in reviews]
    
    return render(request, "tunementor/client.html", {
        "profile": profile,
        "reviews": reviews,
        "avr_rating": f"{avr_rating:.2f}" if avr_rating is not None else "None",
        "reviewers": reviewers
    })


@csrf_exempt
@login_required(login_url='login')
def send_msg(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            sender = request.user
            receiver = User.objects.get(id=data.get("receiver"))
            message = data.get("message")

            if not message:
                return JsonResponse({"message": "Message are required!"}, status=400)

            msg = Message(sender=sender, receiver=receiver, message=message)    
            msg.save()

            return JsonResponse({
                "message": "Message sent succuesfully!",
                "sender": sender.username,
                "receiver": receiver.username
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        
    return JsonResponse({"message": "Invalid request method"}, status=405)


@csrf_exempt
def search(request):
    if request.method == "GET":
        city = request.GET.get("city")
        level = request.GET.get("level")

        query = Q()
        if city:
            query &= Q(city=city)
        if level:
            query &= Q(level=level)

        profiles = InstructorProfile.objects.filter(query).order_by('?')
        profile_list = [profile.serialize() for profile in profiles]

        return JsonResponse({
            "message": "Searched succuesfully",
            "profiles": profile_list
        })
    
    return JsonResponse({"message": "Invalid request method"}, status=405)


@csrf_exempt
@login_required(login_url='login')
def review(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            reviewer = request.user
            instructor_profile = InstructorProfile.objects.get(id=data.get("instructorProfileId")) 
            rating = int(data.get("rating"))
            comment = data.get("comment")

            if rating not in range(1, 6):
                return JsonResponse({"message": "Invalid rating number"}, status=400)
            
            review = Review(reviewer=reviewer, instructor_profile=instructor_profile, rating=rating, comment=comment)
            review.save()

            # Get updated Instructor Profile to extract updated Average Rating
            inst_p = InstructorProfile.objects.get(id=data.get("instructorProfileId"))
            avr_rating = inst_p.get_avr_rating()

            return JsonResponse({
                "message": "Reviewed succesfully",
                "reviewer": reviewer.username,
                "comment": comment,
                "rating": rating,
                "avrRating": avr_rating,
                "reviewId": review.id
            }, status=200)
        
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        
        except IntegrityError:
            return JsonResponse({"message": "The user already submitted a review for this instructor"}, status=400)
        
        except InstructorProfile.DoesNotExist:
            return JsonResponse({"message": "Instructor does not exist"}, status=404)

    return JsonResponse({"message": "Invalid request method"}, status=405)


@csrf_exempt
@login_required(login_url='login')
def editReview(request):
    if request.method == "PUT":
        try:
            data = json.loads(request.body)
            review_id = data.get("reviewId")
            edited_comment = data.get("editedComment")
            edited_rating = data.get("editedRating")

            review = Review.objects.get(id=review_id)
            review.comment = edited_comment
            review.rating = edited_rating
            review.save()

            avr_rating = review.instructor_profile.get_avr_rating()

            return JsonResponse({
                "message": "Review updated succesfully",
                "editedComment": edited_comment,
                "editedRating": edited_rating,
                "avrRating": avr_rating
            })
        
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        
        except Review.DoesNotExist:
            return JsonResponse({"message": "Review does not exist"}, status=404)
        
    return JsonResponse({"message": "Invalid request method"}, status=405)


@login_required(login_url='login')
def message(request, id):
    if request.user.id != int(id):
        return HttpResponse("Invalid request", status=403)

    if request.method == "GET":
        receiver = User.objects.get(id=id)
        msg_objects = Message.objects.filter(receiver=receiver).order_by("-id")

        return render(request, "tunementor/message.html", {
            "msg_objects": msg_objects 
        })
    
    return HttpResponse("Invalid request method", status=400)


@csrf_exempt
@login_required(login_url='login')
def delete_msg(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            message_id = int(data.get("messageId"))
            if not request.user.received_messages.filter(id=message_id).exists():
                return JsonResponse({"message": "You dont have permission to delete this message"}, status=403)
            
            msg_obj = Message.objects.get(id=message_id)
            msg_obj.delete()

            return JsonResponse({"message": "Message deleted succuesfully!"})
        
        except Message.DoesNotExist:
            return JsonResponse({"message": "Message does not exist!"}, status=404)
        
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid json"}, status=400)
        
    return JsonResponse({"message": "Invalid request method"}, status=405)


@login_required(login_url='login')
def change_pass(request, id):
    if request.method == "GET":
        return render(request, "tunementor/change_pass.html", {
            "message": "You are about to change your password"
        })
    
    if request.method == "POST":
        password = request.POST["password"]
        password_new = request.POST["password_new"]
        confirmation = request.POST["confirmation"]

        if request.user.id != id:
            return render(request, "tunementor/change_pass.html", {
                "message": "Invalid request"
            })
        
        if not request.user.check_password(password):
            return render(request, "tunementor/change_pass.html", {
                "message": "Your current password is incorrect"
            })

        if password_new != confirmation:
            return render(request, "tunementor/change_pass.html", {
                "message": "Confirmation is not valid"
            })
        
        request.user.set_password(password_new)
        request.user.save()
        update_session_auth_hash(request, request.user)

        return render(request, "tunementor/change_pass.html", {
                "message": "Password is changed succesfully"
            })
    

@login_required(login_url='login')
def my_profile(request, id):
    if request.user.id != id:
        return render(request, "tunementor/my_profile.html", {
            "message": "Invalid request",
            "profile": None
        })

    try:
        profile = InstructorProfile.objects.get(instructor=request.user)
    except InstructorProfile.DoesNotExist:
        profile = None

    if request.user.role != "instructor":
        return render(request, "tunementor/my_profile.html", {
            "message": "User role must be Instructor",
            "profile": None
        })
    
    if request.method == "GET":
        return render(request, "tunementor/my_profile.html", {
            "message": "You are about to save your profile",
            "profile": profile
        })
    
    if request.method == "POST":
        profile_id = request.POST.get("profile_id")
        bio = request.POST["bio"]
        city = request.POST["city"]
        level = request.POST["level"]

        if city not in [city[0] for city in InstructorProfile.CITY_CHOICES]:
            return render(request, "tunementor/my_profile.html", {
                "message": "Invalid city",
                "profile": profile
            })
        
        if level not in [level[0] for level in InstructorProfile.LEVEL_CHOICES]:
            return render(request, "tunementor/my_profile.html", {
                "message": "Invalid level",
                "profile": profile
            })
        
        if profile_id is None:
            new_profile = InstructorProfile(instructor=request.user, bio=bio, city=city, level=level)
            new_profile.save()
        else:
            existing_profile = InstructorProfile.objects.get(id=profile_id)
            existing_profile.bio = bio
            existing_profile.city = city
            existing_profile.level = level
            existing_profile.save()

        updated_profile = InstructorProfile.objects.get(instructor=request.user)
        return render(request, "tunementor/my_profile.html", {
            "message": "Saved",
            "profile": updated_profile
        })