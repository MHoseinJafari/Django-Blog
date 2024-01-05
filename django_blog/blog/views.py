from rest_framework import viewsets
from .models import Blog,Vote
from . import serializers
from accounts.models import User
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import status
from django.http import HttpResponseRedirect
from django.urls import reverse




class BlogModelViewSet(viewsets.ModelViewSet):

    queryset = Blog.objects.all()
    serializer_class = serializers.BlogSerializer
    

    def update(self, request, pk=None,  *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        vote_obj = self.request.data.get("vote")
        if vote_obj:
            vote_obj = int(vote_obj)
            blog = Blog.objects.get(pk=pk)
            blog.vote_submit(user=self.request.user, amount=vote_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)