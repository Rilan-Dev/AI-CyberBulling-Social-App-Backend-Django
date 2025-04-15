from django.test import TestCase
from django.contrib.auth.models import User
from cyberbullying.models import UserProfile, Post, Comment
from cyberbullying.serializers import (
    UserSerializer, UserProfileSerializer, RegisterSerializer,
    PostSerializer, CommentSerializer, UserProfileUpdateSerializer
)
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIRequestFactory
import json

class UserSerializerTest(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'password123',
            'password2': 'password123'
        }
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
    
    def test_user_serializer(self):
        """Test that a user can be serialized"""
        serializer = UserSerializer(self.user)
        self.assertEqual(serializer.data['username'], 'testuser')
        self.assertEqual(serializer.data['email'], 'test@example.com')
        self.assertEqual(serializer.data['first_name'], 'Test')
        self.assertEqual(serializer.data['last_name'], 'User')
        self.assertNotIn('password', serializer.data)
    
    def test_register_serializer(self):
        """Test that a user can be registered"""
        User.objects.all().delete()  # Clear existing users
        serializer = RegisterSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.check_password('password123'))
    
    def test_register_serializer_password_mismatch(self):
        """Test that passwords must match"""
        data = self.user_data.copy()
        data['password2'] = 'different_password'
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

class UserProfileSerializerTest(TestCase):
    def setUp(self):
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
    
    def test_user_profile_serializer(self):
        """Test that a user profile can be serialized"""
        serializer = UserProfileSerializer(self.profile)
        self.assertEqual(serializer.data['bio'], 'Test bio')
        self.assertEqual(serializer.data['user']['username'], 'testuser')
        self.assertEqual(serializer.data['follower_count'], 0)
        self.assertEqual(serializer.data['following_count'], 0)
    
    def test_user_profile_update_serializer(self):
        """Test that a user profile can be updated"""
        data = {
            'bio': 'Updated bio'
        }
        serializer = UserProfileUpdateSerializer(self.profile, data=data)
        self.assertTrue(serializer.is_valid())
        updated_profile = serializer.save()
        self.assertEqual(updated_profile.bio, 'Updated bio')

class PostSerializerTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.image = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        self.post = Post.objects.create(
            user=self.user,
            content="Test post content",
            image=self.image,
            status="clean",
            confidence=0.95,
            text_analysis=json.dumps({
                "success": True,
                "prediction": "not_cyberbullying",
                "status": "clean",
                "confidence": 0.95,
                "reason": None,
                "processed_text": "test post content"
            }),
            image_analysis=json.dumps({
                "success": True,
                "prediction": "Non_Offensive",
                "status": "clean",
                "confidence": 0.95,
                "reason": None,
                "filename": "test_image.jpg"
            })
        )
        self.request = self.factory.get('/')
        self.request.user = self.user
    
    def test_post_serializer(self):
        """Test that a post can be serialized"""
        serializer = PostSerializer(self.post, context={'request': self.request})
        self.assertEqual(serializer.data['content'], 'Test post content')
        self.assertEqual(serializer.data['status'], 'clean')
        self.assertEqual(serializer.data['confidence'], 0.95)
        self.assertEqual(serializer.data['user']['username'], 'testuser')
        self.assertEqual(serializer.data['like_count'], 0)
        self.assertEqual(serializer.data['is_liked'], False)
        self.assertIsNotNone(serializer.data['text_analysis'])
        self.assertIsNotNone(serializer.data['image_analysis'])

class CommentSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.image = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        self.post = Post.objects.create(
            user=self.user,
            content="Test post content",
            image=self.image,
            status="clean",
            confidence=0.95
        )
        self.comment = Comment.objects.create(
            post=self.post,
            user=self.user,
            content="Test comment content",
            status="clean",
            confidence=0.95
        )
    
    def test_comment_serializer(self):
        """Test that a comment can be serialized"""
        serializer = CommentSerializer(self.comment)
        self.assertEqual(serializer.data['content'], 'Test comment content')
        self.assertEqual(serializer.data['status'], 'clean')
        self.assertEqual(serializer.data['confidence'], 0.95)
        self.assertEqual(serializer.data['user']['username'], 'testuser')
