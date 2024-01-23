from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Avg, Sum
from django.core.validators import MaxValueValidator, MinValueValidator

User = get_user_model()

class Blog(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True, related_name="post_categories")
    rate = models.FloatField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def initiate(self, user):
        vote = Vote.objects.filter(user=user, post = self)
        if vote.exists():
            return Vote.objects.get(user=user, post = self)
        else:
            return Vote.objects.create(user=user, post = self)
    
    def vote_submit(self, user, amount):
            if amount in range(6    ):
                vote_obj = self.initiate(user)
                vote_obj.vote = amount
                vote_obj.save()
                post_rate = self.avrage_vote()
                vote_obj.post.rate = post_rate
                vote_obj.post.save()
                return vote_obj.post.rate
            else:
                raise ValueError("invalid amount")
            
    def avrage_vote(self):
        post_obj = Blog.objects.filter(id=self.id).annotate(avg_vote=Avg("vote__vote"))
        post_rate = post_obj[0].avg_vote
        return post_rate
 

class Category(models.Model):
    name = models.CharField(max_length=30)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='vote')
    vote = models.IntegerField(null=True, blank=True)

    

        
        