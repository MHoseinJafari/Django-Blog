from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Comment(models.Model):
    post = models.ForeignKey("blog.Blog", on_delete=models.CASCADE, related_name='post')
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    reply = models.ForeignKey("Comment", on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return self.post.title