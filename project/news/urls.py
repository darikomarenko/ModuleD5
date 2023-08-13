from django.urls import path, include
from .views import PostList, PostDetail, PostCreateView, PostDeleteView, PostUpdateView, PostSearch

urlpatterns = [
    path('posts', PostList.as_view()),
    path('posts/search', PostSearch.as_view(), name='search'),
    path('posts/<int:pk>', PostDetail.as_view()),
    path('posts/create', PostCreateView.as_view(), name='create'),
    path('posts/<int:pk>/edit', PostUpdateView.as_view(), name='edit'),
    path('posts/<int:pk>/delete', PostDeleteView.as_view(), name='delete'),
]
