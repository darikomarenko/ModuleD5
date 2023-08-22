from django.urls import path

from .views import (
    PostList,
    PostDetail,
    PostCreateView,
    PostDeleteView,
    PostUpdateView,
    PostSearch,
    i_am_author,
    CategoryDetailView,
    subscribe,
    unsubscribe,
)

urlpatterns = [
    path("", PostList.as_view(), name="list"),
    path("search/", PostSearch.as_view(), name="search"),
    path("<int:pk>", PostDetail.as_view(), name="post"),
    path("create", PostCreateView.as_view(), name="create"),
    path("<int:pk>/edit", PostUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete", PostDeleteView.as_view(), name="delete"),
    path("be_author/", i_am_author, name="be_author"),
    path("category/<int:pk>", CategoryDetailView.as_view(), name="category"),
    path("category/<int:pk>/subscribe", subscribe, name="subscribe"),
    path("category/<int:pk>/unsubscribe", unsubscribe, name="unsubscribe"),
]
