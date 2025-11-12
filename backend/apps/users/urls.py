from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('push-subscriptions/', views.push_subscriptions, name='push-subscriptions'),
]