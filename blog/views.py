import markdown
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from django.db.models import Count
from django.conf import settings
from django.db.models import Q
from .models import Blog, BlogType
from read_record.utils import read_num_plus


def get_blogs_common(request, blog_listset):
    paginator = Paginator(blog_listset, settings.BLOG_NUMBER_OF_EACH_PAGE)
    page_num = request.GET.get('page', 1)
    page_of_blogs_obj = paginator.get_page(page_num)
    current_num = page_of_blogs_obj.number
    total_page_number = page_of_blogs_obj.paginator.num_pages
    # 显示前两页和后两页
    page_range = list(range(max(current_num-2,1), current_num)) + \
    list(range(current_num, min(current_num+2, total_page_number)+1))
    # 太多页加上省略号
    if current_num-2 > 2:
        page_range.insert(0, '...')
    if total_page_number-current_num > 2:
        page_range.append('...')
    # 插入1和最后一页页码
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != total_page_number:
        page_range.append(total_page_number)
    # 传递日期归档的数量
    blog_archive = Blog.objects.dates("created_time", "month", order='DESC')
    blog_dates = {}
    for blog_date in blog_archive:
        blog_count = Blog.objects.filter(created_time__year = blog_date.year, \
                                        created_time__month = blog_date.month).count()
        blog_dates[blog_date] = blog_count
    context = {}
    context['blogs'] = page_of_blogs_obj.object_list
    context['page_of_blogs_obj'] = page_of_blogs_obj
    context['page_range'] = page_range
    context['total_num'] = blog_listset.count()
    # context['blog_types'] = BlogType.objects.all() 
    context['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog'))  # 新增blog_count属性，特殊方法
    context['blog_dates'] = blog_dates
    return context

def blog_list(request):
    blog_listset = Blog.objects.all()
    context = get_blogs_common(request, blog_listset)
    return render(request,'blog/blog_list.html', context)
    

def blog_type(request, blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    blogs = Blog.objects.filter(blog_type=blog_type)
    context = get_blogs_common(request,blogs)
    context['blog_type'] = blog_type
    return render(request,'blog/blog_type.html', context)


def blog_date(request, year, month):
    blogs = Blog.objects.filter(created_time__year=year, created_time__month=month)
    context = get_blogs_common(request,blogs)
    context['date_display'] = "%s年%s月" %(year,month)
    return render(request,'blog/blog_date.html', context)


def blog_detail(request, blog_pk):
    context = {}
    blog = get_object_or_404(Blog, pk=blog_pk)
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
        ])
    blog.content = md.convert(blog.content)
    read_cookie_key = read_num_plus(request, blog)

    context['previous_blog'] = Blog.objects.filter(created_time__gt=blog.created_time).last()
    context['next_blog'] = Blog.objects.filter(created_time__lt=blog.created_time).first()
    context['blog'] = blog
    context['toc'] = md.toc
    response = render(request, 'blog/blog_detail.html', context)
    response.set_cookie(read_cookie_key, 'true')
    return response


def handle_search(request):
    context={}
    condition = None
    sw = request.GET.get('wd', '').strip()
    if sw != '':
        for word in sw.split(' '):
            if condition is None:
                condition = Q(title__icontains=word)
            else:
                condition = condition | Q(title__icontains=word)
            if condition is not None:
                search_blogs = Blog.objects.filter(condition)
                context = get_blogs_common(request, search_blogs)
    context['search_words'] = sw
    return render(request, 'blog/blog_search.html', context)
