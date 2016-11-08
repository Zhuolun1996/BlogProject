from django.shortcuts import render, redirect
from django.http import HttpResponse
from my_blog.models import Article
from datetime import datetime
from django.http import Http404
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from .forms import LoginForm,ArticleForm

# Create your views here.

def home(request):
    posts = Article.objects.all()
    paginator = Paginator(posts, 5)
    page = request.GET.get('page')
    log_status=request.user.is_authenticated()
    try :
        post_list = paginator.page(page)
    except PageNotAnInteger :
        post_list = paginator.page(1)
    except EmptyPage :
        post_list = paginator.page(paginator.num_pages)
    return render(request, 'home.html', {'post_list' : post_list,'log_status':log_status})


def detail(request, id):
    log_status = request.user.is_authenticated()
    try:
        post = Article.objects.get(id=str(id))
    except Article.DoesNotExist:
        raise Http404
    return render(request, 'post.html', {'post': post,'title':post.title,'log_status':log_status})


def archives(request) :
    log_status = request.user.is_authenticated()
    try:
        post_list = Article.objects.all()
    except Article.DoesNotExist :
        raise Http404
    return render(request, 'archives.html', {'post_list' : post_list,
                                            'error' : False,'log_status':log_status})


def search_tag(request, tag):
    log_status = request.user.is_authenticated()
    try:
        post_list = Article.objects.filter(category__iexact=tag)  # contains
    except Article.DoesNotExist:
        raise Http404
    return render(request, 'tag.html', {'post_list': post_list,'log_status':log_status})


def blog_search(request):
    log_status = request.user.is_authenticated()
    if 'search' in request.GET:
        search_form = request.GET['search']
        if not search_form:
            return render(request, 'home.html')
        else:
            post_list = Article.objects.filter(title__icontains=search_form)
            if len(post_list) == 0:
                return render(request, 'archives.html', {'post_list': post_list,
                                                         'error': True,'log_status':log_status})
            else:
                return render(request, 'archives.html', {'post_list': post_list,
                                                         'error': False,'log_status':log_status})
    return redirect('/')

def login(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request,'login.html', {'form': form})
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                return redirect('/')
            else:
                return render(request,'login.html',{'form': form, 'password_is_wrong': True})
        else:
            return render(request,'login.html', {'form': form})

@login_required(login_url="/login/")
def logout(request):
    auth.logout(request)
    return redirect('/')

@login_required(login_url="/login/")
def makeArticle(request):
    log_status = request.user.is_authenticated()
    if request.method=='GET':
        article = ArticleForm()
        return render(request,'makeBlog.html',{'ArticleForm':article,'log_status':log_status})
    else:
        article = ArticleForm(request.POST)
        if article.is_valid():
            title=request.POST.get('title')
            category=request.POST.get('category')
            date_time=request.POST.get('date_time')
            content=request.POST.get('content')
            Article.objects.create(title=title,category=category,date_time=date_time,content=content)
            return redirect('/')
        else:
            return render(request,'makeBlog.html',{'ArticleForm': article,'log_status':log_status})