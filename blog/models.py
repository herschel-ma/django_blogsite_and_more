from django.db import models
from django.shortcuts import reverse
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField
from mdeditor.fields import MDTextField 
from read_record.models import ReadDetail
from django.contrib.contenttypes.fields import GenericRelation


class BlogType(models.Model):
    type_name = models.CharField(max_length=15)

    def __str__(self):
        return self.type_name
    class Meta:
        verbose_name = "类别"
        verbose_name_plural = "类别"
      

class Blog(models.Model):
    title = models.CharField(max_length=50)
    blog_type = models.ForeignKey(BlogType, on_delete=models.CASCADE)
    # content = RichTextUploadingField()
    content = MDTextField()
    read_details = GenericRelation(ReadDetail)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    last_updated_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "<Blog: %s>"%(self.title)

    def get_url(self):
        return reverse('blog:blog_detail', kwargs={'blog_pk': self.pk})

    class Meta:
        ordering = ['-created_time']
        verbose_name = "博客"
        verbose_name_plural = "博客"

