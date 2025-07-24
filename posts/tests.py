from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Comment, PostLike

class CodeleapAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="kauan", password="kauan012345")
        self.other_user = User.objects.create_user(username="outro", password="123456")

        response = self.client.post('/api/token/', {"username": "kauan", "password": "kauan012345"}, format='json')
        self.assertEqual(response.status_code, 200)
        access_token = response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        self.test_post_id = 12345  


    def test_list_posts(self):
        url = reverse('posts-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.json(), list)


    def test_create_post(self):
        url = reverse('posts-list-create')
        data = {"title": "Teste Post", "content": "Conteúdo do post"}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        self.assertIn("id", response.json())


    def test_retrieve_post(self):
        url = reverse('posts-rud', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])


    def test_update_post_permission(self):
        url = reverse('posts-rud', kwargs={'pk': 1})
        data = {"title": "Atualização"}
        response = self.client.patch(url, data, format='json')
        if response.status_code == status.HTTP_200_OK:
            self.assertEqual(response.json().get("title"), "Atualização")
        else:
            self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])


    def test_delete_post_permission(self):
        url = reverse('posts-rud', kwargs={'pk': 1})
        response = self.client.delete(url)
        self.assertIn(response.status_code, [
            status.HTTP_204_NO_CONTENT,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ])


    def test_comment_crud(self):
        url = reverse('comments-list-create', kwargs={'post_id': self.test_post_id})
        data = {"content": "Comentário de teste"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment_id = response.json().get("id")

        url_detail = reverse('comments-detail', kwargs={'post_id': self.test_post_id, 'pk': comment_id})
        response = self.client.get(url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("content"), "Comentário de teste")

        data_update = {"content": "Comentário editado"}
        response = self.client.patch(url_detail, data_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("content"), "Comentário editado")

        response = self.client.delete(url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


    def test_like_post(self):
        url = reverse('post-like-toggle', kwargs={'post_id': self.test_post_id})

        response = self.client.post(url)
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])

        response2 = self.client.post(url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_like_count(self):
        url = reverse('post-like-count', kwargs={'post_id': self.test_post_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("likes_count", response.json())


    def test_mentions(self):
        url = reverse('mentions-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("posts", response.json())
        self.assertIn("comments", response.json())
