from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class Comment(models.Model):
    post_id = models.IntegerField()  
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username} on post {self.post_id}'
    

class PostLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post_id = models.IntegerField()

    class Meta:
        unique_together = ('user', 'post_id')

    def __str__(self):
        return f'{self.user.username} like post {self.post_id}'


class Mention(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentions_received')
    post_id = models.IntegerField(null=True, blank=True)       
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, null=True, blank=True)  
    mentioned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentions_made')
    created_datetime = models.DateTimeField(auto_now_add=True)
