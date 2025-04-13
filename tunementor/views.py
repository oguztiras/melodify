from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.urls import reverse
from django.db import IntegrityError
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from schedule.models import Event
import datetime
from django.utils import timezone
from django.db.models import Max

from .models import User, InstructorProfile, Message, Review, Conversation, Instrument, InstructorCalendar, Booking
from .forms import InstructorProfileForm, ApprenticeForm

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
                "message": "Invalid credentials."
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

        # Password match check
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "tunementor/register.html", {
                "message": "Passwords must match."
            })
        
        # Role validation
        valid_roles = [choice[0] for choice in User.ROLE_CHOICES]
        if role not in valid_roles:
            return render(request, "tunementor/register.html", {
                "message": "Role must match."
            })
        
        # Check if username or email is already taken
        if User.objects.filter(Q(username=username) | Q(email=email)).exists():
            return render(request, "tunementor/register.html", {
                "message": "Username or email already taken."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password, role=role)
            user.save()
        except IntegrityError:
            return render(request, "tunementor/register.html", {
                "message": "Registration failed. Please try again."
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

    conversation = Conversation.objects.filter(participants=request.user).filter(participants=profile.instructor).first()
    
    return render(request, "tunementor/client.html", {
        "profile": profile,
        "reviews": reviews,
        "avr_rating": f"{avr_rating:.2f}" if avr_rating is not None else "None",
        "reviewers": reviewers,
        "conversation": conversation
    })


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


@login_required(login_url='login')
def conversation_list(request):
    """List all conversations for the current user."""
    conversations = request.user.conversations.annotate(
        last_message_time=Max('messages__timestamp')
    ).order_by('-last_message_time')

    convos = []
    for convo in conversations:
        other = convo.get_other_participant(request.user)
        # Count unread messages (only messages not from the current user)
        unread_count = convo.messages.filter(is_read=False).exclude(sender=request.user).count()
        convos.append({
            "conversation_id": convo.id,
            "participant": other.username if other else "Group Chat",
            "unread_count": unread_count
        })

    return render(request, "tunementor/conversation_list.html", {
        "conversations": convos
    })


@login_required(login_url='login')
def conversation_detail(request, convo_id):
    """Display a conversation with all messages."""
    conversation = get_object_or_404(Conversation, id=convo_id)

    # Check current user is a participant
    if not conversation.participants.filter(id=request.user.id).exists():
        return HttpResponse("Unauthorized", status=403)

    # Mark all unread messages (sent by the other party) as read.
    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    # Fetch messages after the update.
    messages = conversation.messages.order_by("timestamp")

    return render(request, "tunementor/conversation_detail.html", {
        "conversation": conversation,
        "msgs": messages
    })


@login_required(login_url='login')
def send_message(request):
    if request.method == "POST":
        message_text = request.POST.get("message", "").strip()
        if not message_text:
            return HttpResponse("Message text is required.", status=400)
        
        convo = None
        conversation_id = request.POST.get("conversation_id")
        if conversation_id:
            convo = get_object_or_404(Conversation, id=conversation_id)
            # Be sure the current user is a participant of this conversation
            if not convo.participants.filter(id=request.user.id).exists():
                return HttpResponse("Unauthorized", status=403)

        else:
            recipient_id = request.POST.get("recipient_id")
            if not recipient_id:
                return HttpResponse("Either conversation_id or recipient_id must be provided.", status=400)
            recipient = get_object_or_404(User, id=recipient_id)
            # Look for an existing conversation between the two users
            convo = Conversation.objects.filter(participants=request.user).filter(participants=recipient).first()
            if not convo:
                convo = Conversation.objects.create()
                convo.participants.add(request.user, recipient)

        # New message creation in the conversation 
        Message.objects.create(conversation=convo, sender=request.user, message=message_text)
        return HttpResponseRedirect(reverse("conversation_detail", args=[convo.id]))

    return render(request, "tunementor/send_message.html")


@login_required(login_url='login')
def change_pass(request, id):
    if request.method == "GET":
        return render(request, "tunementor/change_pass.html")
    
    if request.method == "POST":
        password = request.POST["password"]
        password_new = request.POST["password_new"]
        confirmation = request.POST["confirmation"]

        if request.user.id != id:
            messages.error(request, "Invalid request")
            return render(request, "tunementor/change_pass.html")
        
        if not request.user.check_password(password):
            messages.error(request, "Your current password is incorrect")
            return render(request, "tunementor/change_pass.html")

        if password_new != confirmation:
            messages.error(request, "Confirmation is not valid")
            return render(request, "tunementor/change_pass.html")
        
        request.user.set_password(password_new)
        request.user.save()
        update_session_auth_hash(request, request.user)

        messages.success(request, "Password is changed succesfully")
        return render(request, "tunementor/change_pass.html")
    

@login_required(login_url='login')
def my_profile(request, id):
    if request.user.id != id:
        messages.error(request, "Invalid request: you can only view your own profile.")
        return redirect("index")
    
    if request.user.role == "instructor":
        try:
            profile = InstructorProfile.objects.get(instructor=request.user)
        except InstructorProfile.DoesNotExist:
            profile = None

        return render(request, "tunementor/my_profile.html", {
        "profile": profile,
        })

    if request.user.role == "apprentice":
        try:
            appr = User.objects.get(id=request.user.id)
        except User.DoesNotExist:
            appr = None
        
        return render(request, "tunementor/my_profile.html", {
        "appr": appr,
        })

 
@login_required(login_url='login')
def submit_review(request, profile_id):
    """
    Handles the submission (or update) of a review for an instructor.
    Only apprentices who have taken a confirmed lesson (i.e. booking confirmed and event already completed)
    with that instructor are allowed to submit reviews.
    """
    instructor_profile = get_object_or_404(InstructorProfile, id=profile_id)

    # Only apprentices can submit reviews
    if request.user.role != "apprentice":
        messages.error(request, "Only apprentices can submit reviews.")
        return redirect('client', id=instructor_profile.id)
    
    # Needed at least one booked and confirmed lesson within user and instructor that has already ended
    has_confirmed_lesson = Booking.objects.filter(
        apprentice=request.user,
        state="confirmed",
        event__creator=instructor_profile.instructor,
        event__end__lt=timezone.now()
    ).exists()
    
    if not has_confirmed_lesson:
        messages.error(request, "You can only submit a review if you have taken a confirmed and made lesson with this instructor.")
        return redirect('client', id=instructor_profile.id)
    
    # Check if a review from this apprentice for this instructor already exists.
    review = Review.objects.filter(reviewer=request.user, instructor_profile=instructor_profile).first()

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment", "").strip()

        if not rating:
            messages.error(request, "Rating is required.")
            return redirect('client', id=instructor_profile.id)
        
        try:
            rating = int(rating)
        except ValueError:
            messages.error(request, "Invalid rating.")
            return redirect('client', id=instructor_profile.id)
        
        if rating not in range(1, 6):
            messages.error(request, "Rating must be between 1 and 5.")
            return redirect('client', id=instructor_profile.id)
        
        if review:
            # Update existing review
            review.rating = rating
            review.comment = comment
            review.save()
            messages.success(request, "Review updated successfully.")
        else:
            # Create new review
            Review.objects.create(
                reviewer=request.user,
                instructor_profile=instructor_profile,
                rating=rating,
                comment=comment
            )
            messages.success(request, "Review submitted successfully.")

        return redirect('client', id=instructor_profile.id)
    
    # For GET requests, render a dedicated review form.
    return render(request, "tunementor/submit_review.html", {
        "instructor_profile": instructor_profile,
        "review": review
    })
    

@login_required(login_url='login')
def my_reviews(request):
    """
    Dedicated page for apprentices to view all the reviews they have written.
    Each review shows the instructor's name as a clickable link to that instructor's client page.
    """
    if request.user.role == "instructor":
        messages.error(request, "Invalid request. Only apprentices can see their reviews.")
        return redirect("index")

    reviews = Review.objects.filter(reviewer=request.user).order_by("-timestamp")
    return render(request, "tunementor/my_reviews.html", {
        "reviews": reviews
    })


@login_required(login_url='login')
def instructor_reviews(request):
    """
    Dedicated page for instructors to view all the reviews they have received.
    Also displays the average rating.
    """
    if request.user.role != "instructor":
        messages.error(request, "Only instructors have access to this page.")
        return redirect("index")
    
    try:
        profile = request.user.instructor_profile
    except InstructorProfile.DoesNotExist:
        messages.error(request, "Your profile is not set up.")
        return redirect("index")

    reviews = profile.get_reviews().order_by("-timestamp")
    avg_rating = profile.get_avr_rating()
    return render(request, "tunementor/instructor_reviews.html", {
        "reviews": reviews,
        "average_rating": avg_rating,
        "profile": profile
    })
    

@login_required(login_url='login')
def update_profile(request):
    if request.user.role == "instructor":
        try:
            profile = request.user.instructor_profile
        except InstructorProfile.DoesNotExist:
            profile = InstructorProfile(instructor=request.user)

        if request.method == "POST":
            form = InstructorProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect("my_profile", id=request.user.id)
        else:
            form = InstructorProfileForm(instance=profile)

        return render(request, "tunementor/update_profile.html", {"form": form})
    
    if request.user.role == "apprentice":
        appr = request.user

        if request.method == "POST":
            form = ApprenticeForm(request.POST, request.FILES, instance=appr)
            if form.is_valid():
                form.save()
                messages.success(request, "Apprentice updated successfully.")
                return redirect("my_profile", id=request.user.id)
        else:
            form = ApprenticeForm(instance=appr)

        return render(request, "tunementor/update_profile.html", {"form": form})


@login_required(login_url='login')
def create_event(request):
    if request.user.role != "instructor":
        messages.error(request, "Invalid request. Only Instructors can create event!")
        return redirect("index")

    if request.method == "POST":
        start_str = request.POST.get("start")
        end_str = request.POST.get("end")
        title = request.POST.get("title", "Available Lesson")

        # Parse the dates and make them timezone aware to make comparison later
        try:
            start = datetime.datetime.strptime(start_str, "%Y-%m-%d %H:%M")
            end = datetime.datetime.strptime(end_str, "%Y-%m-%d %H:%M")
            start = timezone.make_aware(start)
            end = timezone.make_aware(end)
        except ValueError:
            messages.error(request, "Invalid date format. Please use the format YYYY-MM-DD HH:MM.")
            return redirect("create_event")
        
        # Condition 1: Check if the start time is in the future
        if start < timezone.now():
            messages.error(request, "You cannot create an event in the past. Please choose a future date and time.")
            return redirect("create_event")
        
        # Condition 2: End time must be after the start time
        if end <= start:
            messages.error(request, "End time must be after the start time.")
            return redirect("create_event")
        
        # Condition 3: Event duration should not exceed 8 hours
        duration = end - start
        if duration > datetime.timedelta(hours=8):
            messages.error(request, "Event duration cannot exceed 8 hours.")
            return redirect("create_event")

        # Get or create the instructor’s calendar
        calendar, created = InstructorCalendar.objects.get_or_create(
            owner=request.user,
            defaults={"name": f"{request.user.username}'s Calendar", "slug": request.user.username.lower()}
        )

        # Create the event
        Event.objects.create(
            title=title,
            start=start,
            end=end,
            calendar=calendar,
            creator=request.user,
        )
        return redirect("instructor_calendar", instructor_id=request.user.id)
    
    return render(request, "tunementor/create_event.html")


@login_required(login_url='login')
def book_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # If the event is already booked (by any state other than cancellation), reject new bookings.
    if hasattr(event, "booking") and event.booking.state in ["scheduled", "confirmed"]:
        messages.error(request, "This slot is already booked.")
        return redirect("instructor_calendar", instructor_id=event.creator.id)
    
    if request.user.role != "apprentice":
        messages.error(request, "Only apprentices can book lessons.")
        return redirect("instructor_calendar", instructor_id=event.creator.id)
    
    # The booking in a pending ("scheduled") state creation
    Booking.objects.create(event=event, apprentice=request.user)
    messages.success(request, "Slot booked successfully. Waiting for instructor confirmation.")
    return redirect("instructor_calendar", instructor_id=event.creator.id)
    

@login_required(login_url='login')
def instructor_calendar(request, instructor_id):
    if request.user.role == "instructor" and request.user.id != instructor_id:
        messages.error(request, "Invalid user. Only apprentices or Valid Instructor can see the instructor calender")
        return redirect("index")

    instructor = get_object_or_404(User, id=instructor_id, role="instructor")
    calendar = InstructorCalendar.objects.filter(owner=instructor).first()

    if calendar is None:
        if request.user.role == "instructor":
            messages.error(request, "You need the create at least one event first")
            return redirect("create_event")
        if request.user.role == "apprentice":
            messages.error(request, "Instructor has no event!")
            return redirect("index")
    
    events = calendar.event_set.filter(booking__isnull=True).order_by("start")

    return render(request, "tunementor/instructor_calendar.html", {
        "instructor": instructor,
        "calendar": calendar,
        "events": events,
    })


@login_required(login_url='login')
def confirm_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.user.id != booking.event.creator.id:
        messages.error(request, "You are not authorized to confirm this booking.")
        return redirect("instructor_calendar", instructor_id=booking.event.creator.id)
    
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "confirm":
            booking.state = "confirmed"
            booking.confirmed_at = timezone.now()
            booking.save()
            messages.success(request, "Booking confirmed successfully.")

        elif action == "cancel":
            cancellation_reason = request.POST.get("cancellation_reason", "").strip()
            if not cancellation_reason:
                messages.error(request, "Please provide a cancellation reason.")
                return redirect("confirm_booking", booking_id=booking.id)
            booking.state = "cancelled"
            booking.cancellation_reason = cancellation_reason
            booking.save()
            messages.success(request, "Booking cancelled successfully.")

        return redirect("instructor_calendar", instructor_id=request.user.id)
    
    return render(request, "tunementor/confirm_booking.html", {"booking": booking})


@login_required(login_url='login')
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.user not in [booking.apprentice, booking.event.creator]:
        messages.error(request, "You are not authorized to cancel this booking.")
        return redirect("instructor_calendar", instructor_id=booking.event.creator.id)
    
    if request.method == "POST":
        cancellation_reason = request.POST.get("cancellation_reason", "").strip()
        if not cancellation_reason:
            messages.error(request, "Please provide a cancellation reason.")
            return redirect("cancel_booking", booking_id=booking.id)
        booking.state = "cancelled"
        booking.cancellation_reason = cancellation_reason
        booking.save()
        messages.success(request, "Booking cancelled successfully.")
        return redirect("instructor_calendar", instructor_id=booking.event.creator.id)
    
    return render(request, "tunementor/cancel_booking.html", {"booking": booking})


@login_required(login_url='login')
def booked_instructor(request):
    if request.user.role != "instructor":
        messages.error(request, "Only instructors can view their booked events.")
        return redirect("index")
    
    instructor = request.user
    calendar = InstructorCalendar.objects.filter(owner=instructor).first()

    if calendar is None:
        messages.error(request, "You need the create at least one event first")
        return redirect("create_event")

    booked_events = calendar.event_set.filter(booking__isnull=False).order_by("start")

    return render(request, "tunementor/booked_instructor.html", {
        "instructor": instructor,
        "calendar": calendar,
        "events": booked_events,
    })


@login_required(login_url='login')
def booked_apprentice(request):
    if request.user.role != "apprentice":
        messages.error(request, "Only apprentices can view their booked events.")
        return redirect("index")
    
    bookings = Booking.objects.filter(apprentice=request.user).order_by("event__start")

    return render(request, "tunementor/booked_apprentice.html", {
        "bookings": bookings,
    })


@login_required(login_url='login')
def settings(request, user_id):
    user = User.objects.filter(id=user_id).first()
    if user is None or request.user.id != user_id:
        messages.error(request, "Invalid request: you can only view your own settings.")
        return redirect("index")
    
    return render(request, "tunementor/settings.html")
