from .models import Comment, PostLike, Mention, Post
from django.contrib.auth.models import User
import re
import requests
from rest_framework.response import Response
from datetime import datetime

BASE_API_URL = "https://dev.codeleap.co.uk/careers/"


class UsefulFunctions:

    @staticmethod
    def extract_usernames(text):
        return re.findall(r'@(\w+)', text)

    @staticmethod
    def save_mentions(instance, text, mentioned_by):
        usernames = UsefulFunctions.extract_usernames(text)
        for username in usernames:
            try:
                mentioned_user = User.objects.get(username=username)
                Mention.objects.create(
                    user=mentioned_user,
                    post_id=instance.id if hasattr(instance, 'id') else None,
                    comment=instance if hasattr(instance, 'content') else None,
                    mentioned_by=mentioned_by
                )
            except User.DoesNotExist:
                pass

    @staticmethod
    def fetch_posts(request):
        res = requests.get(BASE_API_URL)

        if res.status_code != 200:
            return None, res.status_code

        posts = res.json().get("results", [])

        username = request.query_params.get("username")
        if username:
            posts = [p for p in posts if p.get("username") == username]

        title_filter = request.query_params.get("title")
        if title_filter:
            posts = [
                post for post in posts
                if title_filter.lower() in post.get("title", "").lower()
            ]

        ordering = request.query_params.get("ordering")
        if ordering in ["created", "-created"]:
            reverse = ordering.startswith("-")
            posts.sort(
                key=lambda p: datetime.fromisoformat(p["created"].replace("Z", "+00:00")),
                reverse=reverse
            )

        for post in posts:
            post_id = post.get("id")
            post["likes"] = PostLike.objects.filter(post_id=post_id).count()

        return posts, 200