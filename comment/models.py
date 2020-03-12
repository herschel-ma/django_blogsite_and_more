from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
import threading


class SendMail(threading.Thread):
    def __init__(self, *args, **kwargs):
        self.subject, self.text, self.email = args
        self.fail_silently = kwargs['fail_silently']
        threading.Thread.__init__(self)
        
    def run(self):
        send_mail(self.subject, '', settings.EMAIL_HOST_USER, [self.email], fail_silently=self.fail_silently, html_message=self.text)

class Comment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    text = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)

    root = models.ForeignKey('self',null=True, related_name='root_comments', on_delete=models.CASCADE)
    parent = models.ForeignKey('self',null=True, related_name='parent_comments', on_delete=models.CASCADE)
    reply_to = models.ForeignKey(User, related_name='replies',null=True, on_delete=models.CASCADE)
    def __str__(self):
        return self.text

    def send_a_mail(self):
        # 发送邮件通知
        subject = ''
        email = ''
        if self.parent is None:
            subject = '您的博客有新的评论！'
            email = self.content_object.author.email
        else:
            subject = '您的评论有新的回复！'
            email = self.reply_to.email
        if email != '':
            text = '%s\n<a href="%s">%s</a>' %(self.text, self.content_object.get_url(),'点击查看')
            send_person = SendMail(subject, text, email, fail_silently=False)
            send_person.start()
            
    class Meta:
        verbose_name = "评论"
        verbose_name_plural = "评论"
        ordering = ['created_time']