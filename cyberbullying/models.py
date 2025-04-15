from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    following = models.ManyToManyField(User, related_name='followers', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"

class Post(models.Model):
    STATUS_CHOICES = (
        ('clean', 'Clean'),
        ('flagged', 'Flagged'),
        ('blocked', 'Blocked'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='clean')
    reason = models.TextField(blank=True, null=True)
    confidence = models.FloatField(default=1.0)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # New fields to store analysis reports
    text_analysis = models.JSONField(blank=True, null=True)
    image_analysis = models.JSONField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Post by {self.user.username} ({self.id})"

class Comment(models.Model):
    STATUS_CHOICES = (
        ('clean', 'Clean'),
        ('flagged', 'Flagged'),
        ('blocked', 'Blocked'),
    )
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='clean')
    reason = models.TextField(blank=True, null=True)
    confidence = models.FloatField(default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on post {self.post.id}"

class TextAnalysisResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='text_analyses')
    text = models.TextField()
    prediction = models.CharField(max_length=50)
    confidence = models.FloatField()
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Text Analysis: {self.prediction} ({self.confidence:.2f})"

class ImageAnalysisResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='image_analyses')
    image = models.ImageField(upload_to='analyzed_images/')
    prediction = models.CharField(max_length=50)
    confidence = models.FloatField()
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image Analysis: {self.prediction} ({self.confidence:.2f})"

# Models for ML integration
class Prediction(models.Model):
    input_text = models.TextField()
    output_label = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.output_label}: {self.input_text[:50]}"

class UserPredictModel(models.Model):
    image = models.ImageField(upload_to='predicted_images/')
    label = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image prediction: {self.label or 'Unknown'}"
