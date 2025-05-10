from django import template
from django.db.models import Count
from markdown import markdown
from django.utils.safestring import mark_safe

from ..models import Post, Comment

register = template.Library()


@register.simple_tag()
def total_posts():
    return Post.published.count()


@register.simple_tag()
def total_comments():
    return Comment.objects.filter(active=True).count()


@register.simple_tag()
def latest_post_date():
    return Post.published.last().publish


@register.inclusion_tag("partials/latest_posts.html")
def latest_posts(count=5):
    latest = Post.published.order_by('-publish')[:count]
    context = {
        'latest_posts': latest
    }
    return context

@register.simple_tag()
def most_commented_posts(count=5):
    return Post.published.annotate(comment_count=Count('comments')).order_by('-comment_count')[:count]

@register.filter(name='markdown')
def to_markdown(text):
    return mark_safe(markdown(text))