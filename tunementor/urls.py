from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("<int:id>", views.client, name="client"),
    path("send_msg", views.send_msg, name="send_msg"),
    path("search", views.search, name="search"),
    path("review", views.review, name="review"),
    path("editReview", views.editReview, name="editReview"),
    path("message/<int:id>", views.message, name="message"),
    path("delete_msg", views.delete_msg, name="delete_msg"),
    path("change_pass/<int:id>", views.change_pass, name="change_pass"),
    path("my_profile/<int:id>", views.my_profile, name="my_profile"),
]