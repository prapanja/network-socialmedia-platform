from django.contrib.auth.models import AbstractUser
from django.db import models
# https://stackoverflow.com/questions/8609192/what-is-the-difference-between-null-true-and-blank-true-in-django


from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    profile_pic = models.ImageField(upload_to="profile_pics", null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.user.username


class User(AbstractUser):
    # We have username, email, hashed password.
    pass

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_posts")
    datetime = models.DateTimeField(auto_now_add=True)
    caption = models.TextField()
    image = models.ImageField(upload_to="postimages", null=True, blank=True)

    def __str__(self):
        return f"User: {self.user}, Time: {self.datetime}, Caption: {self.caption}"

    def serialize(self):
        return {
            "id": self.id,
            "username": self.user.username,
            "user": self.user.id,
            "datetime": self.datetime,
            "caption": self.caption,
        }

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE,related_name="likes")
    like_state = models.BooleanField(blank=True, null=True)

    def __str__(self):
        s = f"User: {self.user}"
        s += f"Post: {self.post}"

        return s

class Following(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    user_being_followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    follow_state = models.BooleanField(default=False)

    def __str__(self):
        s = f"User: {self.user}"
        s += f"Post: {self.user_being_followed}"
        s += f"Following: {self.follow_state}"

        return s





