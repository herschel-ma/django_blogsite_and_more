import string
import random
import time
from django.contrib.auth.models import User
from django.contrib import auth 
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from .form import LoginForm, RegForm, NicknameForm, BindEmailForm, ChangePasswordForm, ForgetPasswordForm
from .models import Profile
from django.core.mail import send_mail


def login(request):
    if request.method == "POST":
        data = request.POST
        login_form = LoginForm(data)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))
    else:
        login_form = LoginForm()
    context = {}
    context['login_form'] = login_form
    return render(request, 'userprofile/login.html', context)

def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('from', reverse('home')))

def register(request):
    if request.method == "POST":
        data = request.POST
        reg_form = RegForm(data, request=request)
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username']
            email = reg_form.cleaned_data['email']
            password = reg_form.cleaned_data['password']
            # 创建用户
            user = User.objects.create_user(username, email, password)
            user.save()
            del request.session['register_code'] 
            # 登录用户
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))

    else:
        reg_form = RegForm()
    context = {}
    context['reg_form'] = reg_form
    return render(request, 'userprofile/register.html', context)

def user_info(request):
    return render(request,'userprofile/user_info.html',context={})

def change_nickname(request):
    if request.method == 'POST':
        nickname_form = NicknameForm(request.POST, user=request.user)
        if nickname_form.is_valid():
            nickname = nickname_form.cleaned_data['nickname']
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.nickname = nickname
            profile.save()
            return redirect(request.GET.get('from', reverse('home')))
    else:
        nickname_form = NicknameForm()
    context = {}
    context['title'] = '我的网站|更改昵称'
    context['form_title']= '更改昵称'
    context['nickname_form'] = nickname_form
    context['click_event_name'] = '更改'
    context['back_url'] = request.GET.get('from', reverse('home'))
    return render(request, 'userprofile/nickname.html', context)

def bind_email(request):
    if request.method == 'POST':
        nickname_form = BindEmailForm(request.POST, request=request)
        if nickname_form.is_valid():
            email = nickname_form.cleaned_data['email']
            request.user.email = email
            request.user.save()
            del request.session['bind_email_code']
            return redirect(request.GET.get('from', reverse('home')))
    else:
        nickname_form = BindEmailForm()
    context = {}
    context['form_title']= '绑定邮箱'
    context['nickname_form'] = nickname_form
    context['click_event_name'] = '绑定'
    context['back_url'] = request.GET.get('from', reverse('home'))
    return render(request, 'userprofile/email.html', context)

def send_verify_code(request):
    email = request.GET.get('email', '')
    send_for = request.GET.get('send_for', '')
    data = {}
    if email != '':
        code = ''.join(random.sample(string.ascii_letters + string.digits, 4))
        now = int(time.time())
        send_code_time = request.session.get('send_code_time', 0)
        if now - send_code_time <= 30:
            data['status'] = 'Error'
        else:
            request.session[send_for] = code
            request.session['send_code_time'] = now
            send_mail(
            '绑定邮箱',
            '',
            'maliang_gs@126.com',
            [email],
            fail_silently=False,
            html_message="即将完成!使用下放验证码完成注册。<br><p style='text-align:center;'>验证码：%s</p>"%code
            )
            data['status'] = 'Success'
    else:
        data['status'] = 'Error'
    return JsonResponse(data)

def change_password(request):
    if request.method == 'POST':
        change_password_form = ChangePasswordForm(request.POST, request=request)
        if change_password_form.is_valid():
            new_password = change_password_form.cleaned_data['new_password']
            user = request.user
            user.set_password(new_password)
            user.save()
            auth.logout(request)
            return redirect(reverse('home'))
    else:
        change_password_form = ChangePasswordForm()
    context = {}
    context['title'] = '我的网站|更改密码'
    context['form_title']= '更改密码'
    context['nickname_form'] = change_password_form
    context['click_event_name'] = '修改'
    context['back_url'] = reverse('home')
    return render(request, 'userprofile/change_password.html', context)

def forget_password(request):
    if request.method == 'POST':
        forget_password_form = ForgetPasswordForm(request.POST, request=request)
        if forget_password_form.is_valid():
            email = forget_password_form.cleaned_data['email']
            new_password = forget_password_form.cleaned_data['new_password']
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            del request.session['forget_password_code']
            auth.logout(request)
            return redirect(reverse('userprofile:login'))
    else:
        forget_password_form = ForgetPasswordForm()
    context = {}
    context['title'] = '我的网站|重置密码'
    context['form_title']= '重置密码'
    context['nickname_form'] = forget_password_form
    context['click_event_name'] = '重置'
    context['back_url'] = reverse('home')
    return render(request, 'userprofile/forget_password.html', context)
