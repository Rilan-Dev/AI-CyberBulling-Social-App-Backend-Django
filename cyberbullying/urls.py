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
    path('users/<str:username>/follow/', views.UserFollowView.as_view(), name='user-follow'),
    path('users/<str:username>/unfollow/', views.UserUnfollowView.as_view(), name='user-unfollow'),
    path('users/<str:username>/followers/', views.UserFollowersView.as_view(), name='user-followers'),
    path('users/<str:username>/following/', views.UserFollowingView.as_view(), name='user-following'),
    path('users/<str:username>/posts/', views.UserPostsView.as_view(), name='user-posts'),
    path('users/search/', views.UserSearchView.as_view(), name='user-search'),
    
    # Analysis endpoints
    path('analyze-text/', views.TextAnalysisView.as_view(), name='analyze-text'),
    path('analyze-image/', views.ImageAnalysisView.as_view(), name='analyze-image'),
    path('history/text/', views.TextAnalysisHistoryView.as_view(), name='text-analysis-history'),
    path('history/image/', views.ImageAnalysisHistoryView.as_view(), name='image-analysis-history'),
    
    # Feed endpoint
    path('feed/', views.FeedView.as_view(), name='feed'),
]
