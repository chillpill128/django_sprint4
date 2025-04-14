from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views


app_name = "blog"


urlpatterns = [
    path('', views.BlogListView.as_view(), name='index'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path(
        'profile/<str:slug>/',
        views.ProfileListView.as_view(),
        name='profile'
    ),
    path(
        'category/<slug:slug>/',
        views.CategoryListView.as_view(),
        name='category_posts'
    ),
    path(
        'posts/<int:pk>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path(
        'posts/<int:pk>/comment/',
        views.CommentCreateView.as_view(),
        name='add_comment'
    ),
    path(
        'posts/<int:pk>/edit_comment/<int:slug>/',
        views.CommentUpdateView.as_view(),
        name='edit_comment'
    ),
    path(
        'posts/<int:pk>/delete_comment/<int:slug>/',
        views.CommentDeleteView.as_view(),
        name='delete_comment'
    ),
    path(
        'posts/<int:pk>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post'
    ),
    path(
        'posts/<int:pk>/edit/',
        views.PostUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        'posts/create/',
        login_required(views.PostCreateView.as_view()),
        name='create_post'
    ),
]
