from django import forms
from django.contrib import auth
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username_or_email = forms.CharField(label='用户名或邮箱', required=True, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'请输入用户名或邮箱', 'autofocus':'autofocus'}))
    password = forms.CharField(label='密码', widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'请输入密码'}))

    def clean(self):
        username_or_email = self.cleaned_data['username_or_email']
        password = self.cleaned_data['password']
        user = auth.authenticate(username=username_or_email, password=password)
        if user is None:
            if User.objects.filter(email=username_or_email).exists():
                username = User.objects.get(email=username_or_email).username
                user = auth.authenticate(username=username, password=password)
                if user is not None:
                    self.cleaned_data['user']=user
                    return self.cleaned_data
            raise forms.ValidationError('用户名，邮箱或密码不正确')
        else:
            self.cleaned_data['user'] = user
        return self.cleaned_data

class RegForm(forms.Form):
    username = forms.CharField(label='用户名',max_length=20,min_length=3,widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'请输入3-20位用户名'}))
    email = forms.EmailField(label='邮箱', widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder':'请输入邮箱'}))
    check_code = forms.CharField(label='验证码', required=False, max_length=10, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'”点击发送验证码“到邮箱'}))
    password = forms.CharField(label='密码', min_length=6, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'请输入6位以上密码'}))
    password_again = forms.CharField(label='再次输入密码', min_length=6, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'请再次输入密码'}))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(RegForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('用户名已存在')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('邮箱已存在')
        return email

    def clean_check_code(self):
        check_code = self.cleaned_data.get('check_code', '')
        if check_code.strip() == '':
            raise forms.ValidationError('验证码不能为空')
        register_code = self.request.session.get('register_code', '')
        if not (register_code != '' and check_code == register_code):
            raise forms.ValidationError('验证码不正确')
        return check_code


    def clean_password_again(self):
        password = self.cleaned_data['password']
        password_again = self.cleaned_data['password_again']
        if password != password_again:
            raise forms.ValidationError('两次输入密码不一致')
        return password_again

class NicknameForm(forms.Form):
    nickname = forms.CharField(label='输入昵称', max_length=10, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'请输入新的昵称'}))
    
    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(NicknameForm, self).__init__(*args, **kwargs)
        
    def clean(self):
        if self.user.is_authenticated:
            nickname = self.cleaned_data.get('nickname','').strip('')
            if nickname == '':
                raise forms.ValidationError('昵称输入为空！')
            else:
                return self.cleaned_data
        else:
            raise forms.ValidationError('用户未登录')
    
class BindEmailForm(forms.Form):
    email = forms.EmailField(label='邮箱', widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder':'请输入正确的邮箱'}))
    check_code = forms.CharField(label='验证码', required=False, max_length=10, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'”点击发送验证码“到邮箱'}))
    
    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(BindEmailForm, self).__init__(*args, **kwargs)
        
    def clean(self):
        if self.request.user.is_authenticated:
            self.cleaned_data['user'] = self.request.user
        else:
            raise forms.ValidationError('用户未登录')
        if self.request.user.email != '':
            raise forms.ValidationError('您已绑定邮箱')
        bind_email_code = self.request.session.get('bind_email_code', '')
        check_code = self.cleaned_data.get('check_code', '')
        if not (bind_email_code != '' and check_code == bind_email_code):
            raise forms.ValidationError('验证码不正确')
        return self.cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已被绑定')
        return email 

    def clean_check_code(self):
        check_code = self.cleaned_data.get('check_code', '')
        if check_code.strip() == '':
            raise forms.ValidationError('验证码不能为空')
        return check_code.strip() 

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label='旧密码', min_length=6, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'请输入旧密码'}))
    new_password = forms.CharField(label='新密码', min_length=6, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'请输入6位以上新密码'}))
    new_password_again = forms.CharField(label='再次输入新密码', min_length=6, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'请再次输入新密码'}))
    
    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        
    def clean(self):
        new_password_again = self.cleaned_data.get('new_password_again', '')
        new_password = self.cleaned_data.get('new_password', '')
        if new_password == '' or new_password_again != new_password:
            raise forms.ValidationError('两次密码输入不一致')
        return self.cleaned_data

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password', '')
        if not self.request.user.check_password(old_password):
            raise forms.ValidationError('旧密码错误')
        return old_password


class ForgetPasswordForm(forms.Form):
    email = forms.EmailField(label='邮箱', widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder':'请输入绑定的邮箱'}))
    check_code = forms.CharField(label='验证码', required=False, max_length=10, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'”点击发送验证码“到邮箱'}))
    new_password = forms.CharField(label='新密码', min_length=6, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'请输入6位以上新密码'}))
    new_password_again = forms.CharField(label='再次输入新密码', min_length=6, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'请再次输入新密码'}))
    
    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(ForgetPasswordForm, self).__init__(*args, **kwargs)
        
    def clean(self):
        email = self.cleaned_data.get('email', '')
        check_code = self.cleaned_data.get('check_code', '')
        new_password_again = self.cleaned_data.get('new_password_again', '')
        new_password = self.cleaned_data.get('new_password', '')
        if email != '':
            if User.objects.filter(email=email).exists():
                if check_code == '' or check_code != self.request.session.get('forget_password_code'):
                    raise forms.ValidationError('验证码错误')
                if new_password == '' or new_password_again != new_password:
                    raise forms.ValidationError('两次密码输入不一致')
            else:
                raise forms.ValidationError('该邮箱不存在')
        else:
            raise forms.ValidationError('邮箱不能为空哦')
        return self.cleaned_data

        
