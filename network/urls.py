
from django.urls import path

from . import views

urlpatterns = [
    path("index", views.index, name="index"),
    path("", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("post", views.post, name="post"),
    path("user_posts", views.user_posts, name="user_posts"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("like/<int:post_id>", views.like, name="like"),
    path("dislike/<int:post_id>", views.dislike, name="dislike"),
    path("follow/<str:username>", views.follow, name="follow"),
    path("following", views.following, name="following")
]
