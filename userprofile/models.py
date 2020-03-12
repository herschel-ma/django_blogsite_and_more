from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=20 ,verbose_name='昵称')

    def __str__(self):
        return '<Prfile:%s-%s>'%(self.nickname, self.user)

    class Meta:
        verbose_name = "个人资料"
        verbose_name_plural = "个人资料"
    
def get_nickname(self):
    if Profile.objects.filter(user=self).exists():
        return Profile.objects.get(user=self).nickname
    else:
        return ''

def get_nickname_or_username(self):
    if Profile.objects.filter(user=self).exists():
        return Profile.objects.get(user=self).nickname
    else:
        return self.username

def has_nickname(self):
    return Profile.objects.filter(user=self).exists()

User.get_nickname=get_nickname
User.has_nickname=has_nickname
User.get_nickname_or_username=get_nickname_or_username

