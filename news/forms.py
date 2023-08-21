from django.forms import ModelForm
from .models import Post
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group


class NewsForm(ModelForm):
    class Meta:
        model = Post
        fields = ["author", "text", "title", "type", "category"]


class BasicSignupForm(SignupForm):
    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        basic_group = Group.objects.get_or_create(name="common")[0]
        basic_group.user_set.add(user)
        return user
