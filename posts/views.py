import re
import requests
from rest_framework import status, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.db import models
from .models import Comment, PostLike, Post
from .serializers import CommentSerializer, PostSerializer
from .utils import *


class PostListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        posts, status_code = UsefulFunctions.fetch_posts(request)
        if status_code != 200:
            return Response({"detail": "Erro ao buscar posts"}, status=status_code)
        return Response(posts)

    def post(self, request):
        payload = {
            "username": request.user.username,
            "title": request.data.get("title"),
            "content": request.data.get("content"),
        }

        res = requests.post(BASE_API_URL, json=payload)

        if res.status_code == 201:
            created_post_id = res.json().get("id")

            post_instance = Post(id=created_post_id, content=payload["content"])
            UsefulFunctions.save_mentions(post_instance, payload["content"], request.user)
            return Response(res.json(), status=status.HTTP_201_CREATED)

        return Response(res.json(), status=res.status_code)


class PostRetrieveUpdateDestroyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object_url(self, pk):
        return f"{BASE_API_URL}{pk}/"

    def get_post_data(self, pk):
        res = requests.get(self.get_object_url(pk))
        if res.status_code == 200:
            return res.json()
        return None

    def get(self, request, pk):
        post = self.get_post_data(pk)
        if post:
            return Response(post)
        return Response({"detail": "Post não encontrado"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk):
        post = self.get_post_data(pk)
        if not post:
            return Response({"detail": "Post não encontrado"}, status=status.HTTP_404_NOT_FOUND)

        if post["username"] != request.user.username:
            return Response({"detail": "Você só pode editar seus próprios posts."}, status=status.HTTP_403_FORBIDDEN)

        payload = {}
        if "title" in request.data:
            payload["title"] = request.data["title"]
        if "content" in request.data:
            payload["content"] = request.data["content"]

        if not payload:
            return Response({"detail": "Nada para atualizar"}, status=status.HTTP_400_BAD_REQUEST)

        res = requests.patch(self.get_object_url(pk), json=payload)

        if "content" in payload and res.status_code == 200:
            from .models import Post
            post_instance = Post(id=pk, content=payload["content"])
            UsefulFunctions.save_mentions(post_instance, payload["content"], request.user)

        return Response(res.json(), status=res.status_code)

    def delete(self, request, pk):
        post = self.get_post_data(pk)
        if not post:
            return Response({"detail": "Post não encontrado"}, status=status.HTTP_404_NOT_FOUND)

        if post["username"] != request.user.username:
            return Response({"detail": "Você só pode deletar seus próprios posts."}, status=status.HTTP_403_FORBIDDEN)

        res = requests.delete(self.get_object_url(pk))
        if res.status_code == 204:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Erro ao deletar"}, status=res.status_code)


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return Comment.objects.filter(post_id=post_id).order_by('created_datetime')

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user, post_id=self.kwargs['post_id'])
        UsefulFunctions.save_mentions(instance, instance.content, self.request.user)


class CommentRetrieveUpdateDestroyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_comment(self, post_id, pk):
        return get_object_or_404(Comment, id=pk, post_id=post_id)

    def get(self, request, post_id, pk):
        comment = self.get_comment(post_id, pk)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    def patch(self, request, post_id, pk):
        comment = self.get_comment(post_id, pk)
        if comment.user != request.user:
            return Response({"detail": "Você só pode editar seus próprios comentários."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            UsefulFunctions.save_mentions(comment, serializer.data.get("content"), request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id, pk):
        comment = self.get_comment(post_id, pk)
        if comment.user != request.user:
            return Response({"detail": "Você só pode deletar seus próprios comentários."}, status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PostLikeToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        user = request.user
        like, created = PostLike.objects.get_or_create(user=user, post_id=post_id)
        if created:
            return Response({"detail": "Post curtido"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "Post já estava curtido"}, status=status.HTTP_200_OK)

    def delete(self, request, post_id):
        user = request.user
        try:
            like = PostLike.objects.get(user=user, post_id=post_id)
            like.delete()
            return Response({"detail": "Like removido"}, status=status.HTTP_204_NO_CONTENT)
        except PostLike.DoesNotExist:
            return Response({"detail": "Like não encontrado"}, status=status.HTTP_404_NOT_FOUND)


class PostLikeCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, post_id):
        count = PostLike.objects.filter(post_id=post_id).count()
        return Response({"post_id": post_id, "likes_count": count})


class MentionsListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        username = request.user.username
        pattern = re.compile(rf"@{username}\b", re.IGNORECASE)

        posts, status_code = UsefulFunctions.fetch_posts(request)
        if status_code != 200:
            return Response({"error": "Erro ao buscar posts na API externa."}, status=status_code)

        posts_data = [post for post in posts if pattern.search(post.get("title", "")) or pattern.search(post.get("content", ""))]

        comments_mentions = Comment.objects.filter(content__icontains=f"@{username}")
        comments_data = [
            {
                "id": c.id,
                "post_id": c.post_id,
                "content": c.content
            }
            for c in comments_mentions if pattern.search(c.content)
        ]

        return Response({
            "posts": posts_data,
            "comments": comments_data
        })