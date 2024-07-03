import django_filters
from . import models


class CommentFilter(django_filters.FilterSet):
    class Meta:
        model = models.Comment
        fields = [
            "id",
            "post",
        ]
