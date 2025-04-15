from django.test import TestCase
from django.contrib.auth.models import User
from cyberbullying.models import UserProfile, Post, Comment
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
import json
import tempfile
from PIL import Image
import io

class AuthenticationViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.token_url = reverse('token_obtain_pair')
        self.token_refresh_url = reverse('token_refresh')
        self.token_verify_url = reverse('token_verify')
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'password2': 'password123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_register_view(self):
        """Test that a user can register"""
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(UserProfile.objects.count(), 1)
    
    def test_token_obtain(self):
        """Test that a user can obtain a token"""
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        response = self.client.post(self.token_url, {
            'username': 'testuser',
            'password': 'password123'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_token_refresh(self):
        """Test that a user can refresh a token"""
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        response = self.client.post(self.token_url, {
            'username': 'testuser',
            'password': 'password123'
        }, format='json')
        refresh_token = response.data['refresh']
        
        response = self.client.post(self.token_refresh_url, {
            'refresh': refresh_token
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_token_verify(self):
        """Test that a token can be verified"""
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        response = self.client.post(self.token_url, {
            'username': 'testuser',
            'password': 'password123'
        }, format='json')
        access_token = response.data['access']
        
        response = self.client.post(self.token_verify_url, {
            'token': access_token
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class UserProfileViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        self.profile = UserProfile.objects.get(user=self.user)
        self.profile.bio = "Test bio"
        self.profile.save()
        
        self.me_url = reverse('user-profile')
        self.public_profile_url = reverse('public-user-profile', kwargs={'username': 'testuser'})
        
        # Get token
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'testuser',
            'password': 'password123'
        }, format='json')
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_get_current_user(self):
        """Test that a user can get their profile"""
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Test bio')
        self.assertEqual(response.data['user']['username'], 'testuser')
    
    def test_update_user_profile(self):
        """Test that a user can update their profile"""
        response = self.client.put(self.me_url, {
            'bio': 'Updated bio'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Updated bio')
        
        # Verify the profile was updated in the database
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, 'Updated bio')
    
    def test_get_public_profile(self):
        """Test that a user can get another user's public profile"""
        response = self.client.get(self.public_profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Test bio')
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(response.data['post_count'], 0)
        self.assertEqual(response.data['is_following'], False)

class PostViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create a test image
        image = Image.new('RGB', (100, 100), color='red')
        self.image_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(self.image_file, format='JPEG')
        self.image_file.seek(0)
        
        self.posts_url = reverse('post-list')
        
        # Get token
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'testuser',
            'password': 'password123'
        }, format='json')
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_create_post(self):
        """Test that a user can create a post"""
        with open(self.image_file.name, 'rb') as image_file:
            response = self.client.post(self.posts_url, {
                'content': 'Test post content',
                'image': image_file
            }, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'Test post content')
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(Post.objects.count(), 1)
        
        # Check that analysis reports are included
        self.assertIn('text_analysis', response.data)
        self.assertIn('image_analysis', response.data)
    
    def test_list_posts(self):
        """Test that posts can be listed"""
        # Create a post
        with open(self.image_file.name, 'rb') as image_file:
            self.client.post(self.posts_url, {
                'content': 'Test post content',
                'image': image_file
            }, format='multipart')
        
        response = self.client.get(self.posts_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], 'Test post content')
    
    def test_get_post(self):
        """Test that a post can be retrieved"""
        # Create a post
        with open(self.image_file.name, 'rb') as image_file:
            response = self.client.post(self.posts_url, {
                'content': 'Test post content',
                'image': image_file
            }, format='multipart')
        
        post_id = response.data['id']
        post_url = reverse('post-detail', kwargs={'pk': post_id})
        
        response = self.client.get(post_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Test post content')
        self.assertEqual(response.data['user']['username'], 'testuser')
    
    def test_update_post(self):
        """Test that a post can be updated"""
        # Create a post
        with open(self.image_file.name, 'rb') as image_file:
            response = self.client.post(self.posts_url, {
                'content': 'Test post content',
                'image': image_file
            }, format='multipart')
        
        post_id = response.data['id']
        post_url = reverse('post-detail', kwargs={'pk': post_id})
        
        # Update the post
        with open(self.image_file.name, 'rb') as image_file:
            response = self.client.put(post_url, {
                'content': 'Updated post content',
                'image': image_file
            }, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Updated post content')
        
        # Check that analysis reports are updated
        self.assertIn('text_analysis', response.data)
        self.assertIn('image_analysis', response.data)
    
    def test_delete_post(self):
        """Test that a post can be deleted"""
        # Create a post
        with open(self.image_file.name, 'rb') as image_file:
            response = self.client.post(self.posts_url, {
                'content': 'Test post content',
                'image': image_file
            }, format='multipart')
        
        post_id = response.data['id']
        post_url = reverse('post-detail', kwargs={'pk': post_id})
        
        # Delete the post
        response = self.client.delete(post_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 0)
    
    def test_like_post(self):
        """Test that a post can be liked"""
        # Create a post
        with open(self.image_file.name, 'rb') as image_file:
            response = self.client.post(self.posts_url, {
                'content': 'Test post content',
                'image': image_file
            }, format='multipart')
        
        post_id = response.data['id']
        like_url = reverse('post-like', kwargs={'pk': post_id})
        
        # Like the post
        response = self.client.post(like_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'liked')
        
        # Check that the post is liked
        post_url = reverse('post-detail', kwargs={'pk': post_id})
        response = self.client.get(post_url)
        self.assertEqual(response.data['like_count'], 1)
        self.assertEqual(response.data['is_liked'], True)
        
        # Unlike the post
        response = self.client.post(like_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'unliked')
        
        # Check that the post is unliked
        response = self.client.get(post_url)
        self.assertEqual(response.data['like_count'], 0)
        self.assertEqual(response.data['is_liked'], False)

class CommentViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create a test image
        image = Image.new('RGB', (100, 100), color='red')
        self.image_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(self.image_file, format='JPEG')
        self.image_file.seek(0)
        
        # Get token
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'testuser',
            'password': 'password123'
        }, format='json')
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Create a post
        with open(self.image_file.name, 'rb') as image_file:
            response = self.client.post(reverse('post-list'), {
                'content': 'Test post content',
                'image': image_file
            }, format='multipart')
        
        self.post_id = response.data['id']
        self.comments_url = reverse('comment-list')
    
    def test_create_comment(self):
        """Test that a user can create a comment"""
        response = self.client.post(self.comments_url, {
            'post': self.post_id,
            'content': 'Test comment content'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'Test comment content')
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(Comment.objects.count(), 1)
    
    def test_list_comments(self):
        """Test that comments can be listed"""
        # Create a comment
        self.client.post(self.comments_url, {
            'post': self.post_id,
            'content': 'Test comment content'
        }, format='json')
        
        response = self.client.get(self.comments_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], 'Test comment content')
    
    def test_get_comment(self):
        """Test that a comment can be retrieved"""
        # Create a comment
        response = self.client.post(self.comments_url, {
            'post': self.post_id,
            'content': 'Test comment content'
        }, format='json')
        
        comment_id = response.data['id']
        comment_url = reverse('comment-detail', kwargs={'pk': comment_id})
        
        response = self.client.get(comment_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Test comment content')
        self.assertEqual(response.data['user']['username'], 'testuser')
    
    def test_update_comment(self):
        """Test that a comment can be updated"""
        # Create a comment
        response = self.client.post(self.comments_url, {
            'post': self.post_id,
            'content': 'Test comment content'
        }, format='json')
        
        comment_id = response.data['id']
        comment_url = reverse('comment-detail', kwargs={'pk': comment_id})
        
        # Update the comment
        response = self.client.put(comment_url, {
            'content': 'Updated comment content'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Updated comment content')
    
    def test_delete_comment(self):
        """Test that a comment can be deleted"""
        # Create a comment
        response = self.client.post(self.comments_url, {
            'post': self.post_id,
            'content': 'Test comment content'
        }, format='json')
        
        comment_id = response.data['id']
        comment_url = reverse('comment-detail', kwargs={'pk': comment_id})
        
        # Delete the comment
        response = self.client.delete(comment_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)

class AnalysisViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create a test image
        image = Image.new('RGB', (100, 100), color='red')
        self.image_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(self.image_file, format='JPEG')
        self.image_file.seek(0)
        
        self.text_analysis_url = reverse('analyze-text')
        self.image_analysis_url = reverse('analyze-image')
    
    def test_analyze_text(self):
        """Test that text can be analyzed"""
        response = self.client.post(self.text_analysis_url, {
            'text': 'This is a test text for analysis'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('status', response.data)
        self.assertIn('prediction', response.data)
        self.assertIn('confidence', response.data)
        self.assertIn('processed_text', response.data)
    
    def test_analyze_image(self):
        """Test that an image can be analyzed"""
        with open(self.image_file.name, 'rb') as image_file:
            response = self.client.post(self.image_analysis_url, {
                'image': image_file
            }, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('status', response.data)
        self.assertIn('prediction', response.data)
        self.assertIn('confidence', response.data)
        self.assertIn('filename', response.data)
