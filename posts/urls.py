from django.urls import path
from .views import (
    PostListCreateView,
    PostRetrieveUpdateDestroyView,
    CommentListCreateView,
    CommentRetrieveUpdateDestroyView,
    PostLikeToggleView,
    PostLikeCountView,
    MentionsListView,
)

urlpatterns = [
    path('posts/', PostListCreateView.as_view(), name='posts-list-create'),
    path('posts/<int:pk>/', PostRetrieveUpdateDestroyView.as_view(), name='posts-rud'),

    path('posts/<int:post_id>/comments/', CommentListCreateView.as_view(), name='comments-list-create'),
    path('posts/<int:post_id>/comments/<int:pk>/', CommentRetrieveUpdateDestroyView.as_view(), name='comments-detail'),

    path('posts/<int:post_id>/like/', PostLikeToggleView.as_view(), name='post-like-toggle'),
    path('posts/<int:post_id>/likes/count/', PostLikeCountView.as_view(), name='post-like-count'),

    path('mentions/', MentionsListView.as_view(), name='mentions-list'),
]