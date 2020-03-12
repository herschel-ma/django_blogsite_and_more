from django.urls import path
from . import views

app_name = 'blog'
urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    path('<int:blog_pk>', views.blog_detail, name='blog_detail'),
    path('type/<int:blog_type_pk>', views.blog_type,name='blog_type'),
    path('date/<int:year>/<int:month>', views.blog_date, name='blog_date'),
    path('search', views.handle_search, name='handle_search')
]
