from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Post, Comment, TextAnalysisResult, ImageAnalysisResult
from django.utils import timezone
from django.db.models import Count

class UserSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(source='first_name')
    lastName = serializers.CharField(source='last_name')
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'firstName', 'lastName']
        read_only_fields = ['id']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    post_count = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    website = serializers.URLField(required=False, allow_blank=True)
    location = serializers.CharField(required=False, allow_blank=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)
    
    class Meta:
        
        model = UserProfile
        fields = [
            'id', 'user', 'bio', 'profile_picture', 
            'follower_count', 'following_count', 'post_count',
            'followers', 'following', 'is_following',
            'website', 'location', 'createdAt', 'updatedAt'
        ]
        read_only_fields = ['id', 'createdAt', 'updatedAt']
    
    def get_follower_count(self, obj):
        return obj.user.followers.count()
    
    def get_following_count(self, obj):
        return obj.following.count()
    
    def get_post_count(self, obj):
        return Post.objects.filter(user=obj.user
                                #    status='clean'
                                   ).count()
    
    def get_followers(self, obj):
        # Return a list of users who follow this user
        followers = obj.user.followers.all()
        return UserSerializer(followers, many=True).data
    
    def get_following(self, obj):
        # Return a list of users this user follows
        following = obj.following.all()
        return UserSerializer(following, many=True).data
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.profile.following.filter(id=obj.user.id).exists()
        return False

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(source='user.first_name', required=False)
    lastName = serializers.CharField(source='user.last_name', required=False)
    email = serializers.EmailField(source='user.email', required=False)
    website = serializers.URLField(required=False, allow_blank=True)
    location = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture', 'firstName', 'lastName', 'email', 'website', 'location']
        
    def update(self, instance, validated_data):
        # Handle user data updates
        user_data = validated_data.pop('user', {})
        user = instance.user
        
        if 'first_name' in user_data:
            user.first_name = user_data['first_name']
        if 'last_name' in user_data:
            user.last_name = user_data['last_name']
        if 'email' in user_data:
            user.email = user_data['email']
        
        user.save()
        
        # Handle profile picture upload
        if 'profile_picture' in validated_data:
            instance.profile_picture = validated_data['profile_picture']
        if 'bio' in validated_data:
            instance.bio = validated_data['bio']
        if 'website' in validated_data:
            instance.website = validated_data['website']
        if 'location' in validated_data:
            instance.location = validated_data['location']
            
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
