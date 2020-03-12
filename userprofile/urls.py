from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from . import views

app_name='userprofile'
urlpatterns = [
    path('login/',views.login, name="login"),
    path('logout/',views.logout, name="logout"),
    path('register/',views.register, name="register"),
    path('info/',views.user_info, name="user_info"),
    path('change_nickname/',views.change_nickname, name="change_nickname"),
    path('bind_email/',views.bind_email, name="bind_email"),
    path('change_password/',views.change_password, name="change_password"),
    path('forget_password/',views.forget_password, name="forget_password"),
    path('send_verify_code/',views.send_verify_code, name="send_verify_code"),
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)