from django.http import HttpResponse
from tripmate.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login as auth_login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from .models import Post, Comment
from .forms import PostForm, CommentForm
from django.db.models import Q
from django.contrib.auth import login as auth_login, authenticate
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from .forms import UserProfileForm
from django.contrib import messages
from django.contrib.auth.models import User



# Create your views here.

def index(request):
    return render(request, 'tripmate/homepage.html')

def profile(request):
    return render(request, 'tripmate/profile.html')


def login(request):
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    login(request, user)
                    return redirect(reverse('tripmate:index'))
                else:
                    return HttpResponse("Your Rango account is disabled.")
            else:
                print(f"Invalid login details: {username}, {password}")
                return HttpResponse("Invalid login details supplied.")
    
        else:
            return render(request, 'tripmate/login.html')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            gender = form.cleaned_data.get('gender')
            picture = form.cleaned_data.get('picture') 

            UserProfile.objects.create(user=user, gender=gender, picture=picture)
            messages.success(request, "Registration successful! You can now log in.")
            return redirect('login')
        else: 
            print(form.errors)
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'tripmate/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)  
            return redirect('index')  
    else:
        form = AuthenticationForm()
    return render(request, 'tripmate/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile_view(request):
    user = request.user
    profile = UserProfile.objects.get(user=user)
    friends = profile.friends.all()

    context = {
        'user': user,
        'profile': profile,
        'friends': friends,
    }
    return render(request, 'tripmate/profile.html', context)


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('post_feed')
    else:
        form = PostForm()
    return render(request, 'tripmate/create_post.html', {'form': form})

@login_required
def post_feed(request):
    posts = Post.objects.all().order_by('-created_at')
    comment_form = CommentForm()
    show_only_user = request.GET.get('mine') == '1'
    if show_only_user:
        posts = Post.objects.filter(user=request.user).order_by('-created_at')
    else:
        posts = Post.objects.all().order_by('-created_at')

    return render(request, 'tripmate/feed.html', {
        'posts': posts, 
        'comment_form': comment_form,
        'show_only_user': show_only_user,
        })

@login_required
def add_comment(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
    return redirect('post_feed')


@login_required
def edit_profile_view(request):
    profile = request.user.userprofile

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save(user=request.user)
            return redirect('profile')  # or wherever your profile page is
    else:
        form = UserProfileForm(instance=profile, user=request.user)

    return render(request, 'tripmate/edit_profile.html', {'form': form})


def search_view(request):
    query = request.GET.get('q')
    results = []

    if query:
        results = Post.objects.filter(Q(caption__icontains=query))

    return render(request, 'tripmate/search.html', {
        'query': query,
        'results': results,
    })


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return HttpResponseRedirect(reverse('post_feed'))

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_feed')
    else:
        form = PostForm(instance=post)
    return render(request, 'tripmate/edit_post.html', {'form': form, 'post': post})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    if request.method == 'POST':
        post.delete()
        return redirect('post_feed')
    return render(request, 'tripmate/confirm_delete.html', {'post': post})

@require_POST
@login_required
def ajax_like_post(request):
    post_id = request.POST.get('post_id')
    post = get_object_or_404(Post, id=post_id)

    liked = False
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
        liked = True

    return JsonResponse({
        'liked': liked,
        'like_count': post.total_likes(),
    })

@login_required
def view_user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile = get_object_or_404(UserProfile, user=profile_user)
    current_user_profile = request.user.userprofile
    is_friend = profile in current_user_profile.friends.all()

    user_posts = Post.objects.filter(user=profile_user).order_by('-created_at')
    friends = profile.friends.all()

    return render(request, 'tripmate/view_profile.html', {
        'profile_user': profile_user,
        'profile': profile,
        'is_friend': is_friend,
        'user_posts': user_posts,
        'friends': friends,
    })

@require_POST
@login_required
def add_friend(request, username):
    target_user = get_object_or_404(User, username=username)
    request.user.userprofile.friends.add(target_user.userprofile)
    return redirect('view_profile', username=username)

@require_POST
@login_required
def remove_friend(request, username):
    target_user = get_object_or_404(User, username=username)
    request.user.userprofile.friends.remove(target_user.userprofile)
    return redirect('view_profile', username=username)

@login_required
def user_search_view(request):
    query = request.GET.get('q')
    users = []

    if query:
        users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)

    return render(request, 'tripmate/user_search.html', {
        'query': query,
        'users': users,
    })