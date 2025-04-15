# Cyberbullying Prediction API Documentation

This document provides comprehensive information about the Cyberbullying Prediction API, including endpoints, request/response formats, authentication, and examples.

## Table of Contents

1. [Authentication](#authentication)
2. [Posts](#posts)
3. [Comments](#comments)
4. [Analysis](#analysis)
5. [Users](#users)
6. [Error Handling](#error-handling)

## Authentication

The API uses JWT (JSON Web Token) authentication. To access protected endpoints, you need to include the token in the Authorization header.

### Obtain Token

**Endpoint:** `POST /api/token/`

**Request:**
\`\`\`json
{
  "username": "your_username",
  "password": "your_password"
}
\`\`\`

**Response:**
\`\`\`json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
\`\`\`

### Refresh Token

**Endpoint:** `POST /api/token/refresh/`

**Request:**
\`\`\`json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
\`\`\`

**Response:**
\`\`\`json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
\`\`\`

### Verify Token

**Endpoint:** `POST /api/token/verify/`

**Request:**
\`\`\`json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
\`\`\`

**Response:**
- Status 200 OK if token is valid
- Status 401 Unauthorized if token is invalid

### Register

**Endpoint:** `POST /api/users/register/`

**Request:**
\`\`\`json
{
  "username": "new_user",
  "email": "user@example.com",
  "password": "secure_password",
  "password2": "secure_password",
  "first_name": "John",
  "last_name": "Doe"
}
\`\`\`

**Response:**
\`\`\`json
{
  "user": {
    "id": 1,
    "username": "new_user",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
\`\`\`

## Posts

### List Posts

**Endpoint:** `GET /api/posts`

**Authentication:** Optional

**Query Parameters:**
- `page`: Page number for pagination
- `page_size`: Number of items per page

**Response:**
\`\`\`json
{
  "count": 100,
  "next": "http://example.com/api/posts?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 1,
        "username": "user1",
        "email": "user1@example.com",
        "first_name": "John",
        "last_name": "Doe"
      },
      "content": "This is a sample post",
      "image": "http://example.com/media/post_images/image.jpg",
      "status": "clean",
      "reason": null,
      "confidence": 0.95,
      "like_count": 10,
      "is_liked": false,
      "comments": [],
      "created_at": "2023-01-01T12:00:00Z",
      "text_analysis": {
        "success": true,
        "prediction": "not_cyberbullying",
        "status": "clean",
        "confidence": 0.95,
        "reason": null,
        "processed_text": "this is a sample post"
      },
      "image_analysis": {
        "success": true,
        "prediction": "Non_Offensive",
        "status": "clean",
        "confidence": 0.95,
        "reason": null,
        "filename": "image.jpg"
      }
    }
  ]
}
\`\`\`

### Create Post

**Endpoint:** `POST /api/posts`

**Authentication:** Required

**Content-Type:** `multipart/form-data`

**Request:**
\`\`\`
content: "This is a sample post"
image: [binary file data]
\`\`\`

**Response:**
\`\`\`json
{
  "id": 1,
  "user": {
    "id": 1,
    "username": "user1",
    "email": "user1@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "content": "This is a sample post",
  "image": "http://example.com/media/post_images/image.jpg",
  "status": "clean",
  "reason": null,
  "confidence": 0.95,
  "like_count": 0,
  "is_liked": false,
  "comments": [],
  "created_at": "2023-01-01T12:00:00Z",
  "text_analysis": {
    "success": true,
    "prediction": "not_cyberbullying",
    "status": "clean",
    "confidence": 0.95,
    "reason": null,
    "processed_text": "this is a sample post"
  },
  "image_analysis": {
    "success": true,
    "prediction": "Non_Offensive",
    "status": "clean",
    "confidence": 0.95,
    "reason": null,
    "filename": "image.jpg"
  }
}
\`\`\`

### Get Post

**Endpoint:** `GET /api/posts/{id}`

**Authentication:** Optional

**Response:**
\`\`\`json
{
  "id": 1,
  "user": {
    "id": 1,
    "username": "user1",
    "email": "user1@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "content": "This is a sample post",
  "image": "http://example.com/media/post_images/image.jpg",
  "status": "clean",
  "reason": null,
  "confidence": 0.95,
  "like_count": 10,
  "is_liked": false,
  "comments": [
    {
      "id": 1,
      "post": 1,
      "user": {
        "id": 2,
        "username": "user2",
        "email": "user2@example.com",
        "first_name": "Jane",
        "last_name": "Smith"
      },
      "content": "This is a comment",
      "status": "clean",
      "reason": null,
      "confidence": 0.95,
      "created_at": "2023-01-01T12:30:00Z"
    }
  ],
  "created_at": "2023-01-01T12:00:00Z",
  "text_analysis": {
    "success": true,
    "prediction": "not_cyberbullying",
    "status": "clean",
    "confidence": 0.95,
    "reason": null,
    "processed_text": "this is a sample post"
  },
  "image_analysis": {
    "success": true,
    "prediction": "Non_Offensive",
    "status": "clean",
    "confidence": 0.95,
    "reason": null,
    "filename": "image.jpg"
  }
}
\`\`\`

### Update Post

**Endpoint:** `PUT /api/posts/{id}`

**Authentication:** Required (must be the post owner)

**Content-Type:** `multipart/form-data`

**Request:**
\`\`\`
content: "Updated post content"
image: [binary file data]
\`\`\`

**Response:**
\`\`\`json
{
  "id": 1,
  "user": {
    "id": 1,
    "username": "user1",
    "email": "user1@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "content": "Updated post content",
  "image": "http://example.com/media/post_images/new_image.jpg",
  "status": "clean",
  "reason": null,
  "confidence": 0.95,
  "like_count": 10,
  "is_liked": false,
  "comments": [],
  "created_at": "2023-01-01T12:00:00Z",
  "text_analysis": {
    "success": true,
    "prediction": "not_cyberbullying",
    "status": "clean",
    "confidence": 0.95,
    "reason": null,
    "processed_text": "updated post content"
  },
  "image_analysis": {
    "success": true,
    "prediction": "Non_Offensive",
    "status": "clean",
    "confidence": 0.95,
    "reason": null,
    "filename": "new_image.jpg"
  }
}
\`\`\`

### Partial Update Post

**Endpoint:** `PATCH /api/posts/{id}`

**Authentication:** Required (must be the post owner)

**Content-Type:** `multipart/form-data` or `application/json`

**Request:**
\`\`\`json
{
  "content": "Updated post content"
}
\`\`\`

**Response:**
\`\`\`json
{
  "id": 1,
  "user": {
    "id": 1,
    "username": "user1",
    "email": "user1@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "content": "Updated post content",
  "image": "http://example.com/media/post_images/image.jpg",
  "status": "clean",
  "reason": null,
  "confidence": 0.95,
  "like_count": 10,
  "is_liked": false,
  "comments": [],
  "created_at": "2023-01-01T12:00:00Z",
  "text_analysis": {
    "success": true,
    "prediction": "not_cyberbullying",
    "status": "clean",
    "confidence": 0.95,
    "reason": null,
    "processed_text": "updated post content"
  },
  "image_analysis": {
    "success": true,
    "prediction": "Non_Offensive",
    "status": "clean",
    "confidence": 0.95,
    "reason": null,
    "filename": "image.jpg"
  }
}
\`\`\`

### Delete Post

**Endpoint:** `DELETE /api/posts/{id}`

**Authentication:** Required (must be the post owner)

**Response:**
- Status 204 No Content

### Like/Unlike Post

**Endpoint:** `POST /api/posts/{id}/like`

**Authentication:** Required

**Response:**
\`\`\`json
{
  "status": "liked"
}
\`\`\`
or
\`\`\`json
{
  "status": "unliked"
}
\`\`\`

## Comments

### List Comments

**Endpoint:** `GET /api/comments`

**Authentication:** Required

**Query Parameters:**
- `post_id`: Filter comments by post ID
- `page`: Page number for pagination
- `page_size`: Number of items per page

**Response:**
\`\`\`json
{
  "count": 50,
  "next": "http://example.com/api/comments?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "post": 1,
      "user": {
        "id": 2,
        "username": "user2",
        "email": "user2@example.com",
        "first_name": "Jane",
        "last_name": "Smith"
      },
      "content": "This is a comment",
      "status": "clean",
      "reason": null,
      "confidence": 0.95,
      "created_at": "2023-01-01T12:30:00Z"
    }
  ]
}
\`\`\`

### Create Comment

**Endpoint:** `POST /api/comments`

**Authentication:** Required

**Request:**
\`\`\`json
{
  "post": 1,
  "content": "This is a comment"
}
\`\`\`

**Response:**
\`\`\`json
{
  "id": 1,
  "post": 1,
  "user": {
    "id": 2,
    "username": "user2",
    "email": "user2@example.com",
    "first_name": "Jane",
    "last_name": "Smith"
  },
  "content": "This is a comment",
  "status": "clean",
  "reason": null,
  "confidence": 0.95,
  "created_at": "2023-01-01T12:30:00Z"
}
\`\`\`

### Get Comment

**Endpoint:** `GET /api/comments/{id}`

**Authentication:** Required

**Response:**
\`\`\`json
{
  "id": 1,
  "post": 1,
  "user": {
    "id": 2,
    "username": "user2",
    "email": "user2@example.com",
    "first_name": "Jane",
    "last_name": "Smith"
  },
  "content": "This is a comment",
  "status": "clean",
  "reason": null,
  "confidence": 0.95,
  "created_at": "2023-01-01T12:30:00Z"
}
\`\`\`

### Update Comment

**Endpoint:** `PUT /api/comments/{id}`

**Authentication:** Required (must be the comment owner)

**Request:**
\`\`\`json
{
  "content": "Updated comment"
}
\`\`\`

**Response:**
\`\`\`json
{
  "id": 1,
  "post": 1,
  "user": {
    "id": 2,
    "username": "user2",
    "email": "user2@example.com",
    "first_name": "Jane",
    "last_name": "Smith"
  },
  "content": "Updated comment",
  "status": "clean",
  "reason": null,
  "confidence": 0.95,
  "created_at": "2023-01-01T12:30:00Z"
}
\`\`\`

### Delete Comment

**Endpoint:** `DELETE /api/comments/{id}`

**Authentication:** Required (must be the comment owner)

**Response:**
- Status 204 No Content

## Analysis

### Analyze Text

**Endpoint:** `POST /api/analyze-text`

**Authentication:** Optional

**Request:**
\`\`\`json
{
  "text": "This is a sample text for analysis"
}
\`\`\`

**Response:**
\`\`\`json
{
  "success": true,
  "status": "clean",
  "prediction": "not_cyberbullying",
  "confidence": 0.95,
  "reason": null,
  "processed_text": "this is a sample text for analysis"
}
\`\`\`

**Response (Flagged Content):**
\`\`\`json
{
  "success": true,
  "status": "flagged",
  "prediction": "age",
  "confidence": 0.78,
  "reason": "Content contains age-based discrimination or bullying",
  "processed_text": "this is a flagged text for analysis"
}
\`\`\`

**Response (Blocked Content):**
\`\`\`json
{
  "success": true,
  "status": "blocked",
  "prediction": "ethnicity",
  "confidence": 0.92,
  "reason": "Content contains ethnicity-based discrimination or hate speech",
  "processed_text": "this is a blocked text for analysis"
}
\`\`\`

### Analyze Image

**Endpoint:** `POST /api/analyze-image`

**Authentication:** Optional

**Content-Type:** `multipart/form-data`

**Request:**
\`\`\`
image: [binary file data]
\`\`\`

**Response:**
\`\`\`json
{
  "success": true,
  "prediction": "Non_Offensive",
  "status": "clean",
  "confidence": 0.95,
  "reason": null,
  "filename": "image.jpg"
}
\`\`\`

**Response (Flagged Content):**
\`\`\`json
{
  "success": true,
  "prediction": "negative",
  "status": "flagged",
  "confidence": 0.72,
  "reason": "Image contains negative content that may be upsetting",
  "filename": "image.jpg"
}
\`\`\`

**Response (Blocked Content):**
\`\`\`json
{
  "success": true,
  "prediction": "offensive",
  "status": "blocked",
  "confidence": 0.89,
  "reason": "Image contains offensive content that violates community guidelines",
  "filename": "image.jpg"
}
\`\`\`

## Users

### Get Current User

**Endpoint:** `GET /api/users/me/`

**Authentication:** Required

**Response:**
\`\`\`json
{
  "id": 1,
  "user": {
    "id": 1,
    "username": "user1",
    "email": "user1@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "bio": "This is my bio",
  "profile_picture": "http://example.com/media/profile_pics/pic.jpg",
  "follower_count": 10,
  "following_count": 20,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-02T00:00:00Z"
}
\`\`\`

### Update User Profile

**Endpoint:** `PUT /api/users/me/`

**Authentication:** Required

**Content-Type:** `multipart/form-data`

**Request:**
\`\`\`
bio: "Updated bio"
profile_picture: [binary file data]
\`\`\`

**Response:**
\`\`\`json
{
  "bio": "Updated bio",
  "profile_picture": "http://example.com/media/profile_pics/new_pic.jpg"
}
\`\`\`

### Get Public User Profile

**Endpoint:** `GET /api/users/{username}/`

**Authentication:** Optional

**Response:**
\`\`\`json
{
  "id": 1,
  "user": {
    "id": 1,
    "username": "user1",
    "email": "user1@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "bio": "This is my bio",
  "profile_picture": "http://example.com/media/profile_pics/pic.jpg",
  "follower_count": 10,
  "following_count": 20,
  "post_count": 15,
  "is_following": false,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-02T00:00:00Z"
}
\`\`\`

## Feed

### Get Feed

**Endpoint:** `GET /api/feed/`

**Authentication:** Required

**Response:**
\`\`\`json
[
  {
    "id": 1,
    "user": {
      "id": 1,
      "username": "user1",
      "email": "user1@example.com",
      "first_name": "John",
      "last_name": "Doe"
    },
    "content": "This is a sample post",
    "image": "http://example.com/media/post_images/image.jpg",
    "status": "clean",
    "reason": null,
    "confidence": 0.95,
    "like_count": 10,
    "is_liked": false,
    "comments": [],
    "created_at": "2023-01-01T12:00:00Z",
    "text_analysis": {
      "success": true,
      "prediction": "not_cyberbullying",
      "status": "clean",
      "confidence": 0.95,
      "reason": null,
      "processed_text": "this is a sample post"
    },
    "image_analysis": {
      "success": true,
      "prediction": "Non_Offensive",
      "status": "clean",
      "confidence": 0.95,
      "reason": null,
      "filename": "image.jpg"
    }
  }
]
\`\`\`

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of a request.

### Common Status Codes

- **200 OK**: The request was successful
- **201 Created**: The resource was successfully created
- **204 No Content**: The request was successful but there is no content to return
- **400 Bad Request**: The request was invalid or cannot be served
- **401 Unauthorized**: Authentication is required or has failed
- **403 Forbidden**: The authenticated user does not have permission to access the resource
- **404 Not Found**: The requested resource does not exist
- **405 Method Not Allowed**: The HTTP method is not supported for the requested resource
- **500 Internal Server Error**: An error occurred on the server

### Error Response Format

\`\`\`json
{
  "error": "Error title",
  "detail": "Detailed error message"
}
\`\`\`

### Validation Error Format

\`\`\`json
{
  "field_name": [
    "Error message for field"
  ]
}
\`\`\`

Example:
\`\`\`json
{
  "username": [
    "This field is required."
  ],
  "password": [
    "This field is required."
  ]
}
\`\`\`

## Prediction Categories

### Text Analysis

The text analysis endpoint can return the following prediction categories:

- **not_cyberbullying**: The text does not contain cyberbullying content
- **age**: The text contains age-based discrimination or bullying
- **ethnicity**: The text contains ethnicity-based discrimination or hate speech
- **religion**: The text contains religion-based discrimination or offensive material

### Image Analysis

The image analysis endpoint can return the following prediction categories:

- **humour**: The image contains humorous content
- **Non_Offensive**: The image does not contain offensive content
- **negative**: The image contains negative content that may be upsetting
- **offensive**: The image contains offensive content that violates community guidelines
- **NSFW_Content**: The image contains inappropriate content not suitable for all audiences

## Status Categories

Both text and image analysis can result in the following status categories:

- **clean**: The content does not contain cyberbullying indicators
- **flagged**: The content contains potential cyberbullying indicators but is not severe enough to be blocked
- **blocked**: The content contains cyberbullying indicators and would be blocked from being posted

## Confidence Score

The confidence score is a value between 0 and 1 that indicates the model's confidence in its prediction. A higher value indicates higher confidence.
\`\`\`

Now, let's create automated tests for the API:

```python file="backend/cyberbullying/tests/test_models.py"
from django.test import TestCase
from django.contrib.auth.models import User
from cyberbullying.models import UserProfile, Post, Comment, TextAnalysisResult, ImageAnalysisResult
from django.core.files.uploadedfile import SimpleUploadedFile
import json

class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.profile = UserProfile.objects.get(user=self.user)
    
    def test_profile_creation(self):
        """Test that a profile is automatically created when a user is created"""
        self.assertEqual(UserProfile.objects.count(), 1)
        self.assertEqual(self.profile.user, self.user)
    
    def test_profile_str(self):
        """Test the string representation of a profile"""
        self.assertEqual(str(self.profile), "testuser's profile")
    
    def test_following(self):
        """Test the following relationship"""
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='password123'
        )
        self.profile.following.add(user2)
        self.assertEqual(self.profile.following.count(), 1)
        self.assertTrue(user2 in self.profile.following.all())

class PostModelTest(TestCase):
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
    
    def test_post_creation(self):
        """Test that a post can be created"""
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(self.post.user, self.user)
        self.assertEqual(self.post.content, "Test post content")
        self.assertEqual(self.post.status, "clean")
    
    def test_post_str(self):
        """Test the string representation of a post"""
        self.assertEqual(str(self.post), f"Post by testuser ({self.post.id})")
    
    def test_post_likes(self):
        """Test the likes relationship"""
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='password123'
        )
        self.post.likes.add(user2)
        self.assertEqual(self.post.likes.count(), 1)
        self.assertTrue(user2 in self.post.likes.all())
    
    def test_post_analysis_fields(self):
        """Test the analysis fields"""
        self.assertIsNotNone(self.post.text_analysis)
        self.assertIsNotNone(self.post.image_analysis)

class CommentModelTest(TestCase):
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
    
    def test_comment_creation(self):
        """Test that a comment can be created"""
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(self.comment.user, self.user)
        self.assertEqual(self.comment.post, self.post)
        self.assertEqual(self.comment.content, "Test comment content")
        self.assertEqual(self.comment.status, "clean")
    
    def test_comment_str(self):
        """Test the string representation of a comment"""
        self.assertEqual(str(self.comment), f"Comment by testuser on post {self.post.id}")

class AnalysisResultModelTest(TestCase):
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
        self.text_analysis = TextAnalysisResult.objects.create(
            user=self.user,
            text="Test text",
            prediction="not_cyberbullying",
            confidence=0.95
        )
        self.image_analysis = ImageAnalysisResult.objects.create(
            user=self.user,
            image=self.image,
            prediction="Non_Offensive",
            confidence=0.95
        )
    
    def test_text_analysis_creation(self):
        """Test that a text analysis result can be created"""
        self.assertEqual(TextAnalysisResult.objects.count(), 1)
        self.assertEqual(self.text_analysis.user, self.user)
        self.assertEqual(self.text_analysis.text, "Test text")
        self.assertEqual(self.text_analysis.prediction, "not_cyberbullying")
        self.assertEqual(self.text_analysis.confidence, 0.95)
    
    def test_image_analysis_creation(self):
        """Test that an image analysis result can be created"""
        self.assertEqual(ImageAnalysisResult.objects.count(), 1)
        self.assertEqual(self.image_analysis.user, self.user)
        self.assertEqual(self.image_analysis.prediction, "Non_Offensive")
        self.assertEqual(self.image_analysis.confidence, 0.95)
    
    def test_text_analysis_str(self):
        """Test the string representation of a text analysis result"""
        self.assertEqual(str(self.text_analysis), "Text Analysis: not_cyberbullying (0.95)")
    
    def test_image_analysis_str(self):
        """Test the string representation of an image analysis result"""
        self.assertEqual(str(self.image_analysis), "Image Analysis: Non_Offensive (0.95)")
