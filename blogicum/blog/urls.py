from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views


app_name = "blog"


urlpatterns = [
    path('', views.BlogListView.as_view(), name='index'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path(
        'profile/<str:username>/',
        views.ProfileListView.as_view(),
        name='profile'
    ),
    path(
        'category/<slug:category>/',
        views.CategoryListView.as_view(),
        name='category_posts'
    ),
    path(
        'posts/<int:post_id>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path(
        'posts/<int:post_id>/comment/',
        views.CommentCreateView.as_view(),
        name='add_comment'
    ),
    path(
        'posts/<int:post_id>/edit_comment/<int:comment_id>/',
        views.CommentUpdateView.as_view(),
        name='edit_comment'
    ),
    path(
        'posts/<int:post_id>/delete_comment/<int:comment_id>/',
        views.CommentDeleteView.as_view(),
        name='delete_comment'
    ),
    path(
        'posts/<int:post_id>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post'
    ),
    path(
        'posts/<int:post_id>/edit/',
        views.PostUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        'posts/create/',
        login_required(views.PostCreateView.as_view()),
        name='create_post'
    ),
]
