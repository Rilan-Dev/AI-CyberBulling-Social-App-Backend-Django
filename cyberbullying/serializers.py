from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Post, Comment, TextAnalysisResult, ImageAnalysisResult
from django.utils import timezone

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'bio', 'profile_picture', 
            'follower_count', 'following_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_follower_count(self, obj):
        return obj.following.count()
    
    def get_following_count(self, obj):
        return obj.following.count()

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture']
        
    def update(self, instance, validated_data):
        # Handle profile picture upload
        if 'profile_picture' in validated_data:
            instance.profile_picture = validated_data['profile_picture']
        if 'bio' in validated_data:
            instance.bio = validated_data['bio']
        instance.save()
        return instance

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name']
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'email': {'required': True}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user)
        return user

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'content', 'status', 'reason', 'confidence', 'created_at']
        read_only_fields = ['id', 'user', 'status', 'reason', 'confidence', 'created_at']

    def to_representation(self, instance):
        # This ensures the user field is always included in the response
        representation = super().to_representation(instance)
        representation['user'] = UserSerializer(instance.user).data
        return representation

class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    text_analysis = serializers.JSONField(read_only=True)
    image_analysis = serializers.JSONField(read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'user', 'content', 'image', 'status', 'reason', 'confidence', 
                  'like_count', 'is_liked', 'comments', 'created_at',
                  'text_analysis', 'image_analysis']  # Added analysis fields
        read_only_fields = ['id', 'user', 'status', 'reason', 'confidence', 'created_at',
                           'text_analysis', 'image_analysis']
        extra_kwargs = {
            'content': {'required': False},
            'image': {'required': True}
        }
    
    def get_like_count(self, obj):
        return obj.likes.count()
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

    def to_representation(self, instance):
        # This ensures the user field is always included in the response
        representation = super().to_representation(instance)
        representation['user'] = UserSerializer(instance.user).data
        return representation

# Add a new serializer specifically for Swagger documentation of file uploads
class PostCreateUpdateSerializer(serializers.Serializer):
    content = serializers.CharField(required=False, help_text="Post content text")
    image = serializers.ImageField(required=True, help_text="Image file to upload")
    
    class Meta:
        ref_name = "PostCreateUpdate"

# Add a serializer for partial updates where image is optional
class PostPartialUpdateSerializer(serializers.Serializer):
    content = serializers.CharField(required=False, help_text="Post content text")
    image = serializers.ImageField(required=False, help_text="Image file to upload")
    
    class Meta:
        ref_name = "PostPartialUpdate"
