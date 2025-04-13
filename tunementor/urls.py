from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("<int:id>", views.client, name="client"),
    path("search", views.search, name="search"),
    path("change_pass/<int:id>", views.change_pass, name="change_pass"),
    path("my_profile/<int:id>", views.my_profile, name="my_profile"),
    path("conversation_list", views.conversation_list, name="conversation_list"),
    path("conversation_detail/<int:convo_id>", views.conversation_detail, name="conversation_detail"),
    path("send_message", views.send_message, name="send_message"),
    path("submit_review/<int:profile_id>", views.submit_review, name="submit_review"),
    path("my_reviews", views.my_reviews, name="my_reviews"),
    path("instructor_reviews", views.instructor_reviews, name="instructor_reviews"),
    path('update_profile', views.update_profile, name='update_profile'),
    path('calendar/<int:instructor_id>/', views.instructor_calendar, name='instructor_calendar'),
    path('create_event/', views.create_event, name='create_event'),
    path('book_event/<int:event_id>/', views.book_event, name='book_event'),
    path('confirm_booking/<int:booking_id>/', views.confirm_booking, name='confirm_booking'),
    path('cancel_booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('booked_instructor/', views.booked_instructor, name='booked_instructor'),
    path('booked_apprentice/', views.booked_apprentice, name='booked_apprentice'),
    path('settings/<int:user_id>/', views.settings, name='settings'),
]