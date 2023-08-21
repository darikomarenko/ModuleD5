from datetime import datetime, timezone
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum


class Author(models.Model):
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE)
    ratingAutor = models.SmallIntegerField(default=0)

    def update_rating(self):
        postRat = self.post_set.all().aggregate(postrating=Sum("rating"))
        pRat = 0
        pRat += postRat.get("postRating")

        commentRat = self.authorUser.comment_set.all().aggregate(
            postrating=Sum("rating")
        )
        cRat = 0
        cRat += commentRat.get("commentRating")

        self.ratingAuthor = pRat * 3 + cRat
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)
    subscriber = models.ManyToManyField(User, through="CategorySubscribers")


class CategorySubscribers(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE)


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    NEWS = "NW"
    ARTICLE = "AR"
    POST_TYPE = (
        (NEWS, "Новость"),
        (ARTICLE, "Статья"),
    )
    type = models.CharField(max_length=2, choices=POST_TYPE, default=ARTICLE)
    dateCreation = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category)
    title = models.CharField(max_length=128)
    text = models.TextField()
    rating = models.SmallIntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[0:123] + "..."

    def __str__(self):
        return f"{self.title.title()}: {self.text[:50]}  {self.dateCreation} "

    def get_absolute_url(self):
        return f"/posts/{self.id}"


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    commentPost = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comment_post"
    )
    commentUser = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comment_user"
    )
    text = models.TextField()
    dateCreation = models.DateTimeField(auto_now_add=True)
    rating = models.SmallIntegerField(default=0)

    def __str__(self):
        return self.commentUser.username

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()


models.FloatField(default=0.0)
