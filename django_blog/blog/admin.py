from django.contrib import admin
from .models import Blog, Category, Vote
from comment.models import Comment

class CommentInline(admin.TabularInline):
    model = Comment


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    inlines = [
        CommentInline,
    ]



admin.site.register(Category)
admin.site.register(Vote)