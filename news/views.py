from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    DeleteView,
    UpdateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .filters import NewsFilter
from .forms import NewsForm
from .models import Post, Category
from django.core.paginator import Paginator

import logging

logger = logging.getLogger("django")


class PostList(ListView):
    model = Post
    template_name = "postlist.html"
    context_object_name = "posts"
    ordering = ["-dateCreation"]
    paginate_by = 4
    form_class = NewsForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = NewsFilter(self.request.GET, queryset=self.get_queryset())

        context["form"] = self.form_class()
        context["is_not_authors"] = not self.request.user.groups.filter(
            name="authors"
        ).exists()
        return context

    def post(self, request, *args, **kwargs):
        form = self.NewsForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("news")
        else:
            context = self.get_context_data(**kwargs)
            context["form"] = form
            return self.render_to_response(context)


@login_required
def i_am_author(request):
    user = request.user
    authors_group = Group.objects.get(name="authors")
    if not request.user.groups.filter(name="authors").exists():
        authors_group.user_set.add(user)
    return redirect("/posts")


class PostDetail(DetailView):
    model = Post
    template_name = "post.html"
    context_object_name = "post"


class PostCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "news.add_post"
    template_name = "create.html"
    form_class = NewsForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        self.object = form.save()

        post_categories = self.object.category.all()

        for category in post_categories:
            for subscriber in category.subscriber.all():
                html_content = render_to_string(
                    "send_mail_subscribe_to_news.html",
                    {
                        "user": subscriber,
                        "post": self.object,
                    },
                )

                msg = EmailMultiAlternatives(
                    subject=f"{self.object.title}",
                    body=self.object.text,
                    from_email="dariastore@yandex.ru",
                    to=[f"{subscriber.email}"],
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()

        return HttpResponseRedirect(self.get_success_url())


class PostDetailView(DetailView):
    model = Post
    template_name = "post.html"
    context_object_name = "post"
    queryset = Post.objects.all()


class PostUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "news.update_post"
    template_name = "create.html"
    form_class = NewsForm

    def get_object(self, **kwargs):
        id = self.kwargs.get("pk")
        return Post.objects.get(pk=id)


class PostDeleteView(DeleteView):
    template_name = "delete.html"
    queryset = Post.objects.all()
    success_url = reverse_lazy("news:list")


class PostSearch(ListView):
    model = Post
    template_name = "search.html"
    context_object_name = "search"
    ordering = ["-dateCreation"]
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = NewsFilter(self.request.GET, queryset=self.get_queryset())
        return context


class CategoryDetailView(DetailView):
    model = Category
    template_name = "category.html"
    context_object_name = "category"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = Category.objects.get(id=self.kwargs["pk"])
        context["subscribers"] = category.subscriber.all()
        return context


@login_required
def subscribe(request, pk):
    category = Category.objects.get(pk=pk)
    category.subscriber.add(request.user.id)
    return HttpResponseRedirect(reverse("news:category", args=[pk]))


@login_required
def unsubscribe(request, pk):
    category = Category.objects.get(pk=pk)
    category.subscriber.remove(request.user.id)
    return HttpResponseRedirect(reverse("news:category", args=[pk]))
