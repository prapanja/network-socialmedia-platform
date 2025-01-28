from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from .models import Post, User, Like, Following,Profile
from django.conf import settings
from django.db.models import Count, Avg

# from django.contrib.auth.models import User

def index(request):
    posts = Post.objects.all().order_by("-datetime")  # Fetch posts ordered by newest
    return render(request, "index.html", {"Posts": posts})

@login_required
def comment_post(request, post_id):
    """
    Handle adding a comment to a post.
    """
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get("comment", "").strip()

        if content:
            Comment.objects.create(post=post, user=request.user, content=content)

        return redirect('profile', username=request.user.username)

def login_view(request):

    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        print(username)
        password = request.POST["password"]
        print(password)
        user = authenticate(username=username, password=password)
        print(user)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return redirect('login')
    else:
        return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect('index')


def register(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        # Create the user with hashed password
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            # password=password  # create_user hashes the password
        )
        user.set_password(password)


        user.save()
        return redirect('login')

    return render(request, "register.html")


# put data here throught fetch put method


@login_required
def post(request, post_id=None):
    if request.method == "POST":
        caption = request.POST.get("caption")
        image = request.FILES.get('image')

        if caption and image:
            curr_user = request.user  # Authenticated user
            post = Post(caption=caption, user=curr_user, image=image)
            post.save()
            return redirect('index')  # Redirect to index to display the new post

    # Fetch all posts for rendering
    posts = Post.objects.all().order_by("-datetime")
    curr_user = request.user  # Authenticated user
    return render(request, "post.html", {"Posts": posts, "curr_user": curr_user})



def user_posts(request):
    users_posts = Post.objects.filter(user=request.user)
    return JsonResponse([post.serialize for post in users_posts], safe=False)

def profile(request, username):

    user = User.objects.get(username=username)
    # user_posts = user_posts.order_by("-datetime").all()
    user_posts = user.user_posts.all().order_by("-datetime").all()

    # Get current user if they are authenticated.
    if user.is_authenticated:
        curr_user = User.objects.get(id=request.user.id)
        # Give correct context for profile page.
        # Denote whether user is following them.
        try:
            follow = Following.objects.get(user=curr_user,user_being_followed=user)

            if follow.follow_state is None:
                is_following = True
            else:
                is_following = follow.follow_state
  
        except ObjectDoesNotExist:
            is_following = False

        return render(request, "profile.html",{
            "posts": user_posts,
            "is_following": is_following,
            "followers": 0,
            "following": 0
        })


from django.shortcuts import render, get_object_or_404
# from django.contrib.auth.models import User

def profile_view(request, username):
    # Get the user object or return a 404 if not found
    user = get_object_or_404(User, username=username)
    
    # Example: Fetch user-related posts if using a Post model
    posts = user.post_set.all()  # Assuming a ForeignKey(User) in Post model

    # Check if the logged-in user is following the profile owner
    is_following = request.user in user.profile.followers.all() if request.user.is_authenticated else False

    context = {
        'profile_user': user,
        'posts': posts,
        'is_following': is_following
    }
    return render(request, 'profile.html', context)


def like(request, post_id):

    # Only logged in users can use this route, should I use the decorator?
    user = User.objects.get(id=request.user.id)
    post = Post.objects.get(id=post_id)
    # Try to create an instance of Like if it exists.
    try:
        like = Like.objects.get(user=request.user, post=post)
    except ObjectDoesNotExist:
        like = Like.objects.create(user=request.user, post=post)

    if like.like_state:
        like.like_state = None
    else:
        like.like_state = True

    like.save(update_fields=["like_state"])

    return render(request, "profile.html",{
        "posts": user_posts
    })

def dislike(request, post_id):

    user = User.objects.get(id=request.user.id)
    post = Post.objects.get(id=post_id)

    try:
        # TODO: What is the difference between using request.user and user?
        # TODO: What does .get return, and what does filter return? 
        # I would assume the Like object with filter, but for some reason I get a query set
        # with get I get what I expect?
        like = Like.objects.get(user=request.user, post=post)
        if not like.like_state:
            like.like_state = None
        else:
            like.like_state = False
        like.like_state = False

    except ObjectDoesNotExist:
        like = Like.objects.create(user=user, post=post)
        like.like_state = False

    like.save(update_fields=["like_state"])
    
    return render(request, "profile.html",{
        "posts": user_posts
    })


def follow(request, username):

    user = User.objects.get(id=request.user.id)
    following = User.objects.get(username=username)

    # Try to instantiate Follow if it already exists in database.
    try:
        follow = Following.objects.get(user=user, user_being_followed=following)
    except ObjectDoesNotExist:
        follow = Following.objects.create(user=user, user_being_followed=following)
    finally:
        # Save the new follow state.
        if request.method == "PUT":
            if follow.follow_state:
                follow.follow_state = False
            else:
                follow.follow_state = True

        follow.save(update_fields=["follow_state"])
        # return JsonResponse({"following":follow.follow_state})

# TODO: This should only be for logged in users
# def following(request):
#     # Get current user.
#     user = User.objects.get(id=request.user.id)
#     # Get all people user follows.
#     following = Following.objects.filter(user=user)
#     # Get all posts from people user follow.
#     followingPosts = Post.objects.filter()

#     return JsonResponse([])
@login_required
def following(request):
    user = User.objects.get(id=request.user.id)
    following_users = Following.objects.filter(user=user, follow_state=True).values_list('user_being_followed', flat=True)
    posts = Post.objects.filter(user__id__in=following_users).order_by('-datetime')
    return render(request, "following.html", {"posts": posts})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        post.delete()
        return redirect('profile', username=request.user.username)
    return redirect('profile', username=request.user.username)

@login_required
def update_profile(request):
    # Ensure the user has a profile
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        bio = request.POST.get("bio", profile.bio)
        profile_pic = request.FILES.get("profile_pic")

        profile.bio = bio
        if profile_pic:
            profile.profile_pic = profile_pic
        profile.save()

        return redirect('profile', username=request.user.username)  # Redirect to the profile page after updating

    return render(request, "update_profile.html", {"profile": profile})

def post_analysis_dashboard(request):
    # Query to get post analysis data
    posts = (
        Post.objects.annotate(
            likes_count=Count("likes"),
            average_likes=Avg("likes__like_state"),
        )
        .order_by("-likes_count")
    )

    return render(request, "dashboard.html", {"posts": posts})