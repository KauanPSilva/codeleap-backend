from rest_framework import serializers
from .models import Post, Comment, PostLike


class PostSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user', 'title', 'content', 'created_datetime']


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)  

    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'content', 'created_datetime']
        read_only_fields = ['id', 'user', 'created_datetime']


class PostLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLike
        fields = ['id', 'user', 'post_id']
        read_only_fields = ['id', 'user', 'post_id']