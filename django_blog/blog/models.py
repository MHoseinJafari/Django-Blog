from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import F
from rest_framework.exceptions import NotAcceptable
from django.db import transaction


User = get_user_model()


class Blog(models.Model):
    title = models.CharField(max_length=30, default="Blog post title")
    content = models.TextField(default="Blog post content")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    count_of_voters = models.IntegerField(default=0)
    category = models.ForeignKey(
        "Category",
        on_delete=models.SET_NULL,
        null=True,
        related_name="post_categories",
    )
    rate = models.FloatField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def initiate(self, user) -> "Vote":
        with transaction.atomic():
            vote = Vote.objects.filter(user=user, post=self)
            if vote.exists():
                return Vote.objects.select_for_update().get(
                    user=user, post=self
                )
            else:
                self.count_of_voters += 1
                return Vote.objects.select_for_update().create(
                    user=user, post=self
                )

    def vote_submit(self, user, amount: int) -> None:
        if amount in range(6):
            current_count_of_voters = self.count_of_voters
            vote_obj = self.initiate(user)
            current_amount = vote_obj.vote
            vote_obj.vote = amount
            vote_obj.save()
            if self.count_of_voters > current_count_of_voters:
                self.rate = (
                    (F("rate") * current_count_of_voters) + vote_obj.vote
                ) / self.count_of_voters
            else:
                self.rate = (
                    ((F("rate") * current_count_of_voters) - current_amount)
                    + amount
                ) / current_count_of_voters
            self.save()
        else:
            raise NotAcceptable({"detail": "invalid vote"})


class Category(models.Model):
    name = models.CharField(max_length=30)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(
        Blog, on_delete=models.CASCADE, related_name="vote"
    )
    vote = models.IntegerField(null=True, blank=True)
