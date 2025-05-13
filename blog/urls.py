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
    path('profile/', views.profile, name='profile'),
    path('profile/create-post/', views.create_post, name='create_post'),
    path('profile/create-post/<int:pk>/', views.edit_post, name='edit_post'),
    path('profile/delete-post/<int:pk>/', views.delete_post, name='delete_post'),
    path('profile/delete-image/<int:pk>/', views.delete_image, name='delete_image'),
    path('login/', views.user_login, name='login'),
]
