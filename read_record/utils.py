import datetime
from .models import ReadNum, ReadDetail
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum

TODAY = timezone.now().date()
def read_num_plus(request, obj):
    ct = ContentType.objects.get_for_model(obj)
    key = "%s_%s_read" % (ct.model, obj.pk)
    if not request.COOKIES.get(key):
        # 总阅读数+1
        readnum, _ = ReadNum.objects.get_or_create(content_type=ct, object_id=obj.pk)
        readnum.read_num += 1
        readnum.save()
        # 当天阅读数+1
        read_detail, _ = ReadDetail.objects.get_or_create(content_type=ct, object_id=obj.pk, date=TODAY)
        read_detail.read_num += 1
        read_detail.save()
    return key

def get_seven_days_read_data(content_type):
    read_sums = []
    dates = []
    for i in range(7, 0,-1):
        date = TODAY-datetime.timedelta(days=i)
        read_details = ReadDetail.objects.filter(content_type=content_type,date=date)
        dates.append(date.strftime(" %m-%d "))
        read_sum = read_details.aggregate(read_sum_result=Sum('read_num'))
        read_sums.append(read_sum['read_sum_result'] or 0)
    return dates, read_sums

def get_today_hot_data(content_type):
    read_details = ReadDetail.objects.filter(content_type=content_type,date=TODAY).order_by('-read_num')
    return read_details[:5]

def get_yesterday_hot_data(content_type):
    date = TODAY-datetime.timedelta(days=1)
    read_details = ReadDetail.objects.filter(content_type=content_type,date=date).order_by('-read_num')
    return read_details[:5]

