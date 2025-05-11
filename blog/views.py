from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.views.generic import ListView, DetailView
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

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


# def post_list(request, category=None):
#     posts = Post.published.all()
#     paginator = Paginator(posts, 5)
#     page_number = request.GET.get('page', 1)
#     try:
#         posts = paginator.page(page_number)
#     except EmptyPage:
#         posts = paginator.page(paginator.num_pages)  # shows the last page
#     except PageNotAnInteger:
#         posts = paginator.page(1)
#
#     context = {
#         'posts': posts,
#     }
#     return render(request, "blog/list.html", context)

class PostListView(ListView):
    # model = Post  by default takes Post.objects.all()
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 5
    template_name = "blog/list.html"


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
            return redirect('blog:ticket')
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
            search_query = SearchQuery(query)
            search_vector = SearchVector('title', weight="A") + SearchVector('description', weight="B")
            # results = Post.published.filter(description__contains=query)
            # results = Post.published.filter(Q(title__icontains=query) | Q(description__icontains=query))
            # results = Post.published.annotate(search=SearchVector('title', 'description')).filter(search=query)
            results = Post.published.annotate(search=search_vector,
                                              rank=SearchRank(search_vector, search_query)).filter(
                search=search_query).order_by('-rank')

    context = {
        'query': query,
        'results': results,
    }
    return render(request, "blog/search.html", context)
