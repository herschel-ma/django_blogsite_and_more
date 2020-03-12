from django import template
from django.core import exceptions
from django.contrib.contenttypes.models import ContentType
from ..models import Comment
from ..form import CommentForm

from read_record.models import ReadNum

register = template.Library()
@register.simple_tag
def get_comment_count(obj):
    content_type = ContentType.objects.get_for_model(obj)
    count = Comment.objects.filter(content_type=content_type, object_id=obj.pk).count()
    return count

@register.simple_tag
def get_comment_form(obj):
    content_type = ContentType.objects.get_for_model(obj)
    return CommentForm(initial={'content_type':content_type.model,'object_id': obj.pk, 'reply_comment_id':0})

@register.simple_tag
def get_comments(obj):
    content_type = ContentType.objects.get_for_model(obj)
    comments = Comment.objects.filter(content_type = content_type , object_id = obj.pk, parent=None)
    return comments.order_by('-created_time')

@register.simple_tag
def get_read_num(obj):
    try:
        content_type = ContentType.objects.get_for_model(obj)
        readnum = ReadNum.objects.get(content_type=content_type, object_id=obj.pk)
        return readnum.read_num
    except exceptions.ObjectDoesNotExist:
            return 0