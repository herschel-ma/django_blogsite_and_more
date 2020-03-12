from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from .models import Comment
from .form import CommentForm
import json

def UpdateComment(request):
    """
    user = request.user
    refer = request.META.get('HTTP_REFERER', reverse('home'))
    if not user.is_authenticated:
        return render(request, 'error.html', {"errmsg": "用户未登录", "redirect_to":refer})
    text = request.POST.get('text', '').strip()
    if text is '':
        return render(request, 'error.html', {"errmsg":"评论内容为空", "redirect_to":refer})
    try:
        object_id = int(request.POST.get('object_id', ''))
        content_type = request.POST.get('content_type')
        model_class = ContentType.objects.get(model=content_type).model_class()
        model_obj = model_class.objects.get(pk=object_id)
    except Exception as e:
        print(e)
        return render(request, 'error.html', {"errmsg":"评论对象不存在", "redirect_to":refer})

    comment = Comment()
    comment.user = user
    comment.text = text
    comment.content_object = model_obj
    comment.save()
    return redirect(refer)
    """
    comment_form = CommentForm(request.POST, user=request.user)
    refer = request.META.get('HTTP_REFERER', reverse('home'))
    data = {}
    if comment_form.is_valid():
        # 通过检查，保存数据
        comment = Comment()
        comment.user = comment_form.cleaned_data['user']
        comment.text = comment_form.cleaned_data['text']
        comment.content_object = comment_form.cleaned_data['content_object']
        
        # 判断是否是回复数据
        parent = comment_form.cleaned_data['parent']
        if parent is not None:
            comment.root = parent.root if not parent.root is None else parent
            comment.parent = parent
            comment.reply_to = parent.user
        comment.save()
        # 发送邮件通知
        comment.send_a_mail()
        # 返回数据
        data['status'] = 'Success'
        data['username'] = comment.user.get_nickname_or_username()
        data['text'] = comment.text
        data['created_time'] = comment.created_time.strftime('%Y-%m-%d %H:%M:%S')
        if not parent is None:
            data['reply_to'] = comment.reply_to.get_nickname_or_username()
        else:
            data['reply_to'] = ''
        data['pk'] = comment.pk
        data['root_pk'] = comment.root.pk if not comment.root is None else ""
    else:
        # return render(request, 'error.html', {"errmsg":comment_form.errors, "redirect_to":refer})
        data['status'] = 'Error'
        data['errmsg'] = list(comment_form.errors.values())[0][0]
    return JsonResponse(data)