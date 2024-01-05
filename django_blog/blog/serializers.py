from .models import Blog ,Vote
from comment.models import Comment
from rest_framework import serializers
from accounts.models import User


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['content', 'author', 'reply']

class VoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vote
        fields = ["vote"]

        

class BlogSerializer(serializers.ModelSerializer):
    my_vote = serializers.SerializerMethodField(read_only=False)
    vote = serializers.IntegerField(source = "post",write_only=True, required=False)
    comments = CommentSerializer(many=True, required = False)
    

    class Meta:
        model = Blog
        fields = ['id', 'title', 'content', 'author', 'category', 'rate', 'created_date', 'comments', 'my_vote', 'vote' ]
        read_only_fields = ['author', 'rate']
        no_create_fields = ['vote']

    def get_my_vote(self, obj):
        try:
            vote = Vote.objects.get(post=obj, user= self.context['request'].user)
            serializer = VoteSerializer(instance=vote)
            return serializer.data
        except:
            pass
    
    def create(self, validated_data):
        validated_data['author'] = User.objects.get(id=self.context['request'].user.id)
        return super().create(validated_data)


