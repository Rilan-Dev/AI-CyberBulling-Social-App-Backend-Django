from rest_framework import viewsets, permissions, status, generics, filters, parsers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from django.contrib.auth.models import User
from .models import UserProfile, Post, Comment, TextAnalysisResult, ImageAnalysisResult
from .serializers import (
    UserSerializer, UserProfileSerializer, RegisterSerializer,
    PostSerializer, CommentSerializer, UserProfileUpdateSerializer,
    PostCreateUpdateSerializer, PostPartialUpdateSerializer  # Import the new serializers
)
import requests
from django.conf import settings
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import base64
from .ml_views import text_classification_api as ml_text_api
from .ml_views import image_classification_api as ml_image_api
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.http import HttpRequest

# Import Swagger/OpenAPI decorators
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.db.models import Q


from io import BytesIO
from django.test import RequestFactory

# Authentication Views
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create tokens for the new user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


# Import the method_decorator from django.utils.decorators
from django.utils.decorators import method_decorator
# User Profile Views
@method_decorator(csrf_exempt, name='dispatch')
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = user.profile  # Assuming you have a related profile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile = get_object_or_404(UserProfile, user=request.user)
        serializer = UserProfileUpdateSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class PublicUserProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        profile = get_object_or_404(UserProfile, user=user)
        serializer = UserProfileSerializer(profile)
        
        # Add basic user info and post count
        response_data = serializer.data
        response_data['post_count'] = Post.objects.filter(user=user, status='clean').count()
        response_data['is_following'] = False
        
        if request.user.is_authenticated:
            response_data['is_following'] = request.user.profile.following.filter(id=user.id).exists()
        
        return Response(response_data)

# Post Views
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(status='clean').order_by('-created_at')
    serializer_class = PostSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @swagger_auto_schema(
        operation_description="Create a new post with mandatory image and optional content",
        request_body=PostCreateUpdateSerializer,
        responses={
            201: PostSerializer,
            400: 'Bad Request - Missing image or validation error',
            401: 'Unauthorized'
        }
    )
    def create(self, request, *args, **kwargs):
        # Remove user data if it's in the request
        if 'user' in request.data:
            request.data.pop('user')
        
        # Check if image is provided (mandatory)
        if 'image' not in request.FILES and 'image' not in request.data:
            return Response(
                {"error": "Image is required", "detail": "Please provide an image file"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update a post with mandatory image and optional content",
        request_body=PostCreateUpdateSerializer,
        responses={
            200: PostSerializer,
            400: 'Bad Request - Missing image or validation error',
            401: 'Unauthorized',
            404: 'Not Found'
        }
    )
    def update(self, request, *args, **kwargs):
        # Remove user data if it's in the request
        if 'user' in request.data:
            request.data.pop('user')
        
        # Check if image is provided (mandatory)
        if 'image' not in request.FILES and 'image' not in request.data:
            return Response(
                {"error": "Image is required", "detail": "Please provide an image file"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Partially update a post",
        request_body=PostPartialUpdateSerializer,
        responses={
            200: PostSerializer,
            400: 'Bad Request - Validation error',
            401: 'Unauthorized',
            404: 'Not Found'
        }
    )
    def partial_update(self, request, *args, **kwargs):
        # Remove user data if it's in the request
        if 'user' in request.data:
            request.data.pop('user')
        
        # For partial updates, we don't require the image to be present
        # But if we're updating the post, we should still analyze any new content
        
        return super().partial_update(request, *args, **kwargs)

    # In PostViewSet
    def perform_create(self, serializer):
        # Get content and image from request
        content = self.request.data.get('content', '')
        image = self.request.FILES.get('image')
        
        if not image:
            raise ValidationError({"image": "Image is required"})
        
        # Initialize analysis results
        text_status, text_confidence, text_reason = 'clean', 0.95, None
        image_status, image_confidence, image_reason = 'clean', 0.95, None
        
        # Initialize analysis reports
        text_analysis_report = None
        image_analysis_report = None
        
        # Analyze text content if present
        if content:
            # Forward to ML endpoint
            factory = RequestFactory()
            mock_request = factory.post(
                '/ml/analyze-text/',
                data={'text': content},
                content_type='application/json'
            )
            
            # Call the ML view directly
            response = ml_text_api(mock_request)
            result = json.loads(response.content)
            
            if result.get('success'):
                text_status = result.get('status', 'clean')
                text_confidence = result.get('confidence', 0.95)
                text_reason = result.get('reason')
                
                # Store the full analysis report
                text_analysis_report = result
                
                # Save analysis result
                TextAnalysisResult.objects.create(
                    user=self.request.user,
                    text=content,
                    prediction=result.get('prediction', 'unknown'),
                    confidence=text_confidence,
                    reason=text_reason
                )
        
        # Analyze image (mandatory)
        # Create a mock request to pass to the ML view
        factory = RequestFactory()
        mock_request = factory.post(
            '/ml/analyze-image/',
            {'image': image},
            format='multipart'
        )
        
        # Call the ML view directly
        response = ml_image_api(mock_request)
        result = json.loads(response.content)
        
        if result.get('success'):
            image_status = result.get('status', 'clean')
            image_confidence = result.get('confidence', 0.95)
            image_reason = result.get('reason')
            
            # Store the full analysis report
            image_analysis_report = result
            
            # Save analysis result
            ImageAnalysisResult.objects.create(
                user=self.request.user,
                image=image,
                prediction=result.get('prediction', 'unknown'),
                confidence=image_confidence,
                reason=image_reason
            )
        
        # Determine overall status (use the more restrictive status)
        if text_status == 'blocked' or image_status == 'blocked':
            status_val = 'blocked'
            confidence = max(text_confidence, image_confidence)
            reason = text_reason if text_status == 'blocked' else image_reason
        elif text_status == 'flagged' or image_status == 'flagged':
            status_val = 'flagged'
            confidence = max(text_confidence, image_confidence)
            reason = text_reason if text_status == 'flagged' else image_reason
        else:
            status_val = 'clean'
            confidence = min(text_confidence, image_confidence)
            reason = None
        
        # Save the post with analysis results and the authenticated user
        serializer.save(
            user=self.request.user,
            status=status_val,
            confidence=confidence,
            reason=reason,
            text_analysis=text_analysis_report,
            image_analysis=image_analysis_report
        )

    def perform_update(self, serializer):
        # Get the existing instance
        instance = self.get_object()
        
        # Get content and image from request
        content = self.request.data.get('content', instance.content)
        image = self.request.FILES.get('image')
        
        # For full updates, image is required
        if self.action == 'update' and not image:
            raise ValidationError({"image": "Image is required"})
        
        # Initialize analysis results
        text_status, text_confidence, text_reason = 'clean', 0.95, None
        image_status, image_confidence, image_reason = 'clean', 0.95, None
        
        # Initialize analysis reports
        text_analysis_report = instance.text_analysis  # Keep existing report if not updated
        image_analysis_report = instance.image_analysis  # Keep existing report if not updated
        
        # Analyze text content if it has changed
        if content and content != instance.content:
            # Forward to ML endpoint
            factory = RequestFactory()
            mock_request = factory.post(
                '/ml/analyze-text/',
                data={'text': content},
                content_type='application/json'
            )
            
            # Call the ML view directly
            response = ml_text_api(mock_request)
            result = json.loads(response.content)
            
            if result.get('success'):
                text_status = result.get('status', 'clean')
                text_confidence = result.get('confidence', 0.95)
                text_reason = result.get('reason')
                
                # Store the full analysis report
                text_analysis_report = result
                
                # Save analysis result
                TextAnalysisResult.objects.create(
                    user=self.request.user,
                    text=content,
                    prediction=result.get('prediction', 'unknown'),
                    confidence=text_confidence,
                    reason=text_reason
                )
        
        # Analyze image if a new one is provided
        if image:
            # Create a mock request to pass to the ML view
            factory = RequestFactory()
            mock_request = factory.post(
                '/ml/analyze-image/',
                {'image': image},
                format='multipart'
            )
            
            # Call the ML view directly
            response = ml_image_api(mock_request)
            result = json.loads(response.content)
            
            if result.get('success'):
                image_status = result.get('status', 'clean')
                image_confidence = result.get('confidence', 0.95)
                image_reason = result.get('reason')
                
                # Store the full analysis report
                image_analysis_report = result
                
                # Save analysis result
                ImageAnalysisResult.objects.create(
                    user=self.request.user,
                    image=image,
                    prediction=result.get('prediction', 'unknown'),
                    confidence=image_confidence,
                    reason=image_reason
                )
        
        # Determine overall status (use the more restrictive status)
        if text_status == 'blocked' or image_status == 'blocked':
            status_val = 'blocked'
            confidence = max(text_confidence, image_confidence)
            reason = text_reason if text_status == 'blocked' else image_reason
        elif text_status == 'flagged' or image_status == 'flagged':
            status_val = 'flagged'
            confidence = max(text_confidence, image_confidence)
            reason = text_reason if text_status == 'flagged' else image_reason
        else:
            status_val = 'clean'
            confidence = min(text_confidence, image_confidence)
            reason = None
        
        # Save the post with analysis results and ensure the user remains the same
        serializer.save(
            user=instance.user,
            status=status_val,
            confidence=confidence,
            reason=reason,
            text_analysis=text_analysis_report,
            image_analysis=image_analysis_report
        )

    def _analyze_text(self, text):
        # Default values
        result = {
            'status': 'clean',
            'confidence': 0.95,
            'reason': None
        }
        
        if not text:
            return result
            
        try:
            # Create a mock request to pass to the ML view
            mock_request = HttpRequest()
            mock_request.method = 'POST'
            mock_request.content_type = 'application/json'
            mock_request.body = json.dumps({'text': text}).encode('utf-8')
            
            # Call the ML view directly
            response = ml_text_api(mock_request)
            ml_result = json.loads(response.content)
            
            if ml_result.get('success'):
                result['status'] = ml_result.get('status', 'clean')
                result['confidence'] = ml_result.get('confidence', 0.95)
                result['reason'] = ml_result.get('reason')
                
                # Save analysis result if user is authenticated
                if hasattr(self, 'request') and self.request.user.is_authenticated:
                    TextAnalysisResult.objects.create(
                        user=self.request.user,
                        text=text,
                        prediction=ml_result.get('prediction', 'unknown'),
                        confidence=result['confidence'],
                        reason=result['reason']
                    )
                
        except Exception as e:
            print(f"Error analyzing text: {e}")
            # Fallback to simple analysis
            if any(word in text.lower() for word in ['hate', 'stupid', 'idiot']):
                result['status'] = 'blocked'
                result['confidence'] = 0.92
                result['reason'] = "Detected hate speech and offensive language"
            elif any(word in text.lower() for word in ['dislike', 'not good', 'bad']):
                result['status'] = 'flagged'
                result['confidence'] = 0.78
                result['reason'] = "Potentially negative content detected"
            
        return result

    def _analyze_image(self, image):
        # Default values
        result = {
            'status': 'clean',
            'confidence': 0.95,
            'reason': None
        }
        
        if not image:
            return result
            
        try:
            # Create a mock request to pass to the ML view
            factory = RequestFactory()
            mock_request = factory.post(
                '/ml/analyze-image/',
                {'image': image},
                format='multipart'
            )
            
            # Call the ML view directly
            response = ml_image_api(mock_request)
            ml_result = json.loads(response.content)
            
            if ml_result.get('success'):
                result['status'] = ml_result.get('status', 'clean')
                result['confidence'] = ml_result.get('confidence', 0.95)
                result['reason'] = ml_result.get('reason')
                
                # Save analysis result if user is authenticated
                if hasattr(self, 'request') and self.request.user.is_authenticated:
                    ImageAnalysisResult.objects.create(
                        user=self.request.user,
                        image=image,
                        prediction=ml_result.get('prediction', 'unknown'),
                        confidence=result['confidence'],
                        reason=result['reason']
                    )
                
        except Exception as e:
            print(f"Error analyzing image: {e}")
            # For images, we don't have a simple fallback analysis
            # So we'll just keep the default 'clean' status
            
        return result

    @swagger_auto_schema(
        operation_description="Like or unlike a post",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={},  # Empty properties to show no body is required
        ),
        responses={
            200: openapi.Response(
                description="Like status",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING, description="liked or unliked"),
                    }
                )
            ),
            401: 'Unauthorized',
            404: 'Post not found'
        }
    )
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        # Ignore any user data in the request body
        # The authenticated user is obtained from the token
        post = self.get_object()
        
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
            return Response({'status': 'unliked'})
        else:
            post.likes.add(request.user)
            return Response({'status': 'liked'})

# Comment Views
class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_queryset(self):
        # Return all comments if no post_id is specified
        post_id = self.request.query_params.get('post_id')
        if post_id:
            return Comment.objects.filter(post_id=post_id, status='clean').order_by('created_at')
        return Comment.objects.filter(status='clean').order_by('-created_at')

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['post', 'content'],
            properties={
                'post': openapi.Schema(type=openapi.TYPE_INTEGER, description='Post ID'),
                'content': openapi.Schema(type=openapi.TYPE_STRING, description='Comment content'),
            }
        )
    )
    def create(self, request, *args, **kwargs):
        # Remove user data if it's in the request
        if 'user' in request.data:
            request.data.pop('user')
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'content': openapi.Schema(type=openapi.TYPE_STRING, description='Comment content'),
            }
        )
    )
    def update(self, request, *args, **kwargs):
        # Remove user data if it's in the request
        if 'user' in request.data:
            request.data.pop('user')
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'content': openapi.Schema(type=openapi.TYPE_STRING, description='Comment content'),
            }
        )
    )
    def partial_update(self, request, *args, **kwargs):
        # Remove user data if it's in the request
        if 'user' in request.data:
            request.data.pop('user')
        return super().partial_update(request, *args, **kwargs)

    def perform_create(self, serializer):
        # Analyze content before saving
        content = self.request.data.get('content', '')
        
        status_val, confidence, reason = 'clean', 0.95, None
        
        # Analyze text content
        if content:
            try:
                # Create a mock request to pass to the ML view
                from django.http import HttpRequest
                
                mock_request = HttpRequest()
                mock_request.method = 'POST'
                mock_request.content_type = 'application/json'
                mock_request.body = json.dumps({'text': content}).encode('utf-8')
                
                # Call the ML view directly
                response = ml_text_api(mock_request)
                result = json.loads(response.content)
                
                if result.get('success'):
                    status_val = result.get('status', 'clean')
                    confidence = result.get('confidence', 0.95)
                    reason = result.get('reason')
            except Exception as e:
                print(f"Error analyzing comment text: {e}")
                # Fallback to simple analysis
                if any(word in content.lower() for word in ['hate', 'stupid', 'idiot']):
                    status_val, confidence, reason = 'blocked', 0.92, "Detected hate speech and offensive language"
                elif any(word in content.lower() for word in ['dislike', 'not good', 'bad']):
                    status_val, confidence, reason = 'flagged', 0.78, "Potentially negative content detected"
        
        # Save the comment with analysis results and the authenticated user
        serializer.save(
            user=self.request.user,
            status=status_val,
            confidence=confidence,
            reason=reason
        )

    def perform_update(self, serializer):
        # Get the existing instance
        instance = self.get_object()
        
        # Ensure the user remains the same
        serializer.save(user=instance.user)

# Feed View
class FeedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get posts from users the current user is following
        following_ids = request.user.profile.following.values_list('id', flat=True)
        posts = Post.objects.filter(
            Q(user_id__in=following_ids) | Q(user=request.user),
            status='clean'
        ).order_by('-created_at')
        
        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

# Convert function-based views to class-based views for better Swagger documentation
class TextAnalysisView(APIView):
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Analyze text for cyberbullying content",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['text'],
            properties={
                'text': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            200: openapi.Response(
                description="Analysis result",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'prediction': openapi.Schema(type=openapi.TYPE_STRING),
                        'confidence': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'reason': openapi.Schema(type=openapi.TYPE_STRING),
                        'processed_text': openapi.Schema(type=openapi.TYPE_STRING),
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            ),
            400: 'Bad Request'
        }
    )
    def post(self, request):
        """
        Analyze text for cyberbullying content
        """
        # Get text from either JSON body or form data
        text = None
        if request.content_type == 'application/json':
            text = request.data.get('text', '')
        else:
            text = request.POST.get('text', '')
            if not text:
                text = request.data.get('text', '')
        
        if not text:
            return Response({
                'error': 'Text is required',
                'detail': 'Please provide text to analyze'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Forward to ML endpoint
            factory = RequestFactory()
            mock_request = factory.post(
                '/ml/analyze-text/',
                data={'text': text},
                content_type='application/json'
            )
            
            response = ml_text_api(mock_request)
            result = json.loads(response.content)

            if result.get('success'):
                # Format the response with all needed fields
                response_data = {
                    'success': True,
                    'status': result.get('status', 'clean'),
                    'prediction': result.get('prediction', 'unknown'),
                    'confidence': result.get('confidence', 0.0),
                    'reason': result.get('reason'),
                    'processed_text': result.get('processed_text', text.lower())
                }
                
                # Save analysis result if user is authenticated
                if request.user.is_authenticated:
                    TextAnalysisResult.objects.create(
                        user=request.user,
                        text=text,
                        prediction=result.get('prediction', 'unknown'),
                        confidence=result.get('confidence', 0.0),
                        reason=result.get('reason')
                    )
                
                return Response(response_data)
            
            return Response({
                'success': False,
                'error': 'Analysis failed',
                'detail': result.get('error', 'Unknown error')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Analysis error',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ImageAnalysisView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    
    @swagger_auto_schema(
        operation_description="Analyze image for cyberbullying content",
        manual_parameters=[
            openapi.Parameter(
                'image', 
                openapi.IN_FORM, 
                description="Image file to analyze",
                type=openapi.TYPE_FILE,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Analysis result",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'prediction': openapi.Schema(type=openapi.TYPE_STRING),
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'confidence': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'reason': openapi.Schema(type=openapi.TYPE_STRING),
                        'filename': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: 'Bad Request'
        }
    )
    def post(self, request):
        """
        Analyze image for cyberbullying content
        """
        image = request.FILES.get('image')
        
        if not image:
            return Response({
                'success': False,
                'error': 'Image is required', 
                'detail': 'Please provide an image file to analyze'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Forward directly to ML endpoint
            response = ml_image_api(request)
            result = json.loads(response.content)
            
            if result.get('success'):
                # Format the response with the fields you want to show
                response_data = {
                    'success': True,
                    'prediction': result.get('prediction', 'unknown'),
                    'status': result.get('status', 'clean'),
                    'confidence': result.get('confidence', 0.0),
                    'reason': result.get('reason', 'No reason provided'),
                    'filename': result.get('filename', image.name)
                }
                
                # Save analysis result if user is authenticated
                if request.user.is_authenticated:
                    ImageAnalysisResult.objects.create(
                        user=request.user,
                        image=image,
                        prediction=result.get('prediction', 'unknown'),
                        confidence=result.get('confidence', 0.0),
                        reason=result.get('reason')
                    )
                
                return Response(response_data)
            else:
                # Handle ML API failure
                return Response({
                    'success': False,
                    'error': 'Analysis failed',
                    'detail': result.get('error', 'Unknown error')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Analysis error',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
