from django.urls import path

from . import views

app_name = 'blog'
urlpatterns = [
    path('', views.index, name='index'),
    path('posts/', views.PostListView.as_view(), name='post_list'),
    # path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('posts/<int:pk>/comment/', views.post_comment, name='post_comment'),
    path('tickets/', views.ticket, name='ticket_list'),
    path('search/', views.post_search, name='post_search'),
]