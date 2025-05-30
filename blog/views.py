from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.views.generic import ListView, DetailView
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import *
from .forms import *


# Create your views here.

def index(request):
    # last_post = Post.published.all().order_by('-publish')[0]
    # context = {
    #     "last_post": last_post
    # }
    # return render(request, "blog/index.html", context)
    return render(request, 'blog/index.html')


def post_list(request, category=None):
    if category is not None:
        posts = Post.published.filter(category=category)
    posts = Post.published.all()
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)  # shows the last page
    except PageNotAnInteger:
        posts = paginator.page(1)

    context = {
        'posts': posts,
        'category': category,
    }
    return render(request, "blog/list.html", context)

# class PostListView(ListView):
#     # model = Post  by default takes Post.objects.all()
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 5
#     template_name = "blog/list.html"


def post_detail(request, pk):
    post = get_object_or_404(Post, id=pk, status=Post.Status.PUBLISHED)
    comments = post.comments.filter(active=True)
    form = CommentForm()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, "blog/detail.html", context)


# class PostDetailView(DetailView):
#     model = Post
#     template_name = "blog/detail.html"


def ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            Ticket.objects.create(message=cleaned_data['message'], name=cleaned_data['name'],
                                  email=cleaned_data['email'],
                                  phone=cleaned_data['phone'], subject=cleaned_data['subject'])
            return redirect('blog:ticket_list')
    else:
        form = TicketForm()

    context = {
        'form': form,
    }
    return render(request, "forms/ticket.html", context)


@require_POST
def post_comment(request, pk):
    post = get_object_or_404(Post, id=pk, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid:
        # .save() can be used bcs ModelForm is used
        # commit = False: do not apply changes to DB
        # when using ModelForms no cleaned data is needed
        comment = form.save(commit=False)
        comment.post = post
        comment.save()

    context = {
        'comment': comment,
        'post': post,
        'form': form,
    }
    return render(request, "forms/comment.html", context)


def post_search(request):
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(data=request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # search_query = SearchQuery(query)
            # search_vector = SearchVector('title', weight="A") + SearchVector('description', weight="B")
            # results = Post.published.filter(description__contains=query)
            # results = Post.published.filter(Q(title__icontains=query) | Q(description__icontains=query))
            # results = Post.published.annotate(search=SearchVector('title', 'description')).filter(search=query)
            # results = Post.published.annotate(search=search_vector,
            #                                   rank=SearchRank(search_vector, search_query)).filter(
            #     search=search_query).order_by('-rank')
            results_1 = Post.published.annotate(similarity=TrigramSimilarity('title', query)).filter(
                similarity__gte=0.1).order_by('-similarity')
            results_2 = Post.published.annotate(similarity=TrigramSimilarity('description', query)).filter(
                similarity__gte=0.1).order_by('-similarity')
            results = (results_1 | results_2).order_by('-similarity')

    context = {
        'query': query,
        'results': results,
    }
    return render(request, "blog/search.html", context)


@login_required
def profile(request):
    user = request.user
    posts = Post.published.filter(author=user)

    context = {
        'user': user,
        'posts': posts,
    }
    return render(request, "blog/profile.html", context)


@login_required()
def create_post(request):
    if request.method == 'POST':
        form = CreatePostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            Image.objects.create(image_file=form.cleaned_data['image1'], post=post)
            Image.objects.create(image_file=form.cleaned_data['image2'], post=post)
            return redirect('blog:profile')
    else:
        form = CreatePostForm()

    context = {
        'form': form,
    }
    return render(request, 'forms/create-post.html', context)


@login_required()
def delete_post(request, pk):
    post = get_object_or_404(Post, id=pk, status=Post.Status.PUBLISHED)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile')

    context = {
        'post': post,
    }
    return render(request, 'forms/delete-post.html', context)


@login_required()
def edit_post(request, pk):
    post = get_object_or_404(Post, id=pk, status=Post.Status.PUBLISHED)
    if request.method == 'POST':
        form = CreatePostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            Image.objects.create(image_file=form.cleaned_data['image1'], post=post)
            Image.objects.create(image_file=form.cleaned_data['image2'], post=post)
            return redirect('blog:profile')
    else:
        form = CreatePostForm()

    context = {
        'form': form,
        'post': post,
    }
    return render(request, 'forms/create-post.html', context)


@login_required()
def delete_image(request, pk):
    image = get_object_or_404(Image, id=pk)
    image.delete()
    return redirect('blog:profile')


# def user_login(request):
#     if request == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
#             if user is not None:
#                 if user.is_active:
#                     login(request, user)
#                     return HttpResponse("logged in")
#                 else:
#                     return HttpResponse("not active")
#             else:
#                 return HttpResponse("user does not exist")
#     else:
#         form = LoginForm()
#
#     context = {
#         'form': form
#     }
#     return render(request, "registration/login.html", context)
#

def log_out(request):
    logout(request)
    return redirect(request.META.get('HTTP_REFERER'))


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            Account.objects.create(user=user)
            return render(request, 'registration/register_done.html', {'user': user})
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required()
def edit_account(request):
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        account_form = AccountEditForm(request.post, instance=request.user.account, files=request.FILES)
        if account_form.is_valid() and user_form.is_valid():
            account_form.save()
            user_form.save()
    else:
        user_form = UserEditForm(instance=request.user)
        account_form = AccountEditForm(instance=request.user.account)

    context = {
        'user_form': user_form,
        'account_form': account_form,
    }
    return render(request, "registration/edit_account.html", context)
