from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'), 
    path('post/new/', views.create_post, name='create_post'),
    path('feed/', views.post_feed, name='post_feed'),
    path('comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('search/', views.search_view, name='search'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('ajax/like/', views.ajax_like_post, name='ajax_like_post'),
]