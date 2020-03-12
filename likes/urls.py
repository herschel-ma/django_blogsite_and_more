from django.urls import path
from . import views

app_name = 'likes'
urlpatterns = [
    path('like_change', views.LikeChange, name='like_change')
]
