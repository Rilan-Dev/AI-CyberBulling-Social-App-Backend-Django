from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, ml_views
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Make sure the router is properly configured to handle trailing slashes
# This helps with API consistency
router = DefaultRouter(trailing_slash=False)
router.register(r'posts', views.PostViewSet, basename='post')
router.register(r'comments', views.CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),

    # Authentication endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('users/register/', views.RegisterView.as_view(), name='register'),

    # User endpoints
    path('users/me/', views.UserProfileView.as_view(), name='user-profile'),
    path('users/<str:username>/', views.PublicUserProfileView.as_view(), name='public-user-profile'),
    
    # Analysis endpoints
    path('analyze-text/', views.TextAnalysisView.as_view(), name='analyze-text'),
    path('analyze-image/', views.ImageAnalysisView.as_view(), name='analyze-image'),
    
    # Feed endpoint
    path('feed/', views.FeedView.as_view(), name='feed'),
]
