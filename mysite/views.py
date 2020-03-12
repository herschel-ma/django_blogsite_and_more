import datetime
from django.shortcuts import render, redirect
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from django.core.cache import cache
from blog.models import Blog
from read_record.utils import get_seven_days_read_data, get_today_hot_data \
                                                      , get_yesterday_hot_data

def get_seven_days_hot_read_data():
    today = timezone.now().date()
    date = today-datetime.timedelta(days=7)
    blogs = Blog.objects.filter(read_details__date__lt=today, read_details__date__gte=date)\
                        .values('id', 'title')\
                        .annotate(read_num_sum = Sum('read_details__read_num'))\
                        .order_by('-read_num_sum')
    return blogs[:5]



def home(request):
    context = {}
    ct = ContentType.objects.get_for_model(Blog)  # 通过model名获取对应的ContentType
    dates, read_nums = get_seven_days_read_data(ct)

    get_seven_days_blogs_read_data = cache.get('get_seven_days_blogs_read_data')
    if get_seven_days_blogs_read_data is None:
        data = get_seven_days_hot_read_data()
        cache.set('get_seven_days_blogs_read_data',data, 3600)

    context['dates'] = dates
    context['read_nums'] = read_nums
    context['today_hot_data'] = get_today_hot_data(ct)
    context['get_yesterday_hot_data'] = get_yesterday_hot_data(ct)
    context['get_seven_days_blogs_read_data'] = get_seven_days_hot_read_data
    return render(request,'home.html', context)

