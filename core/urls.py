

from django.urls import path
from knox import views as knox_views
from .views import (
    RegisterAPI, CustomLoginAPI,
    PostCreateAPI, PostListAPI,
    LikePostAPI, UnlikePostAPI,
    SendConnectionRequestAPI, IncomingRequestsAPI,
    AcceptConnectionAPI, RecommendedUsersAPI
)

urlpatterns = [
    # Auth routes
    
    path('register/', RegisterAPI.as_view(), name='register'),
    path('login/', CustomLoginAPI.as_view(), name='login'),
    path('logout/', knox_views.LogoutView.as_view(), name='logout'),

    # Post routes
    path('posts/', PostListAPI.as_view(), name='list-posts'),
    path('posts/create/', PostCreateAPI.as_view(), name='create-post'),
    path('posts/<int:post_id>/like/', LikePostAPI.as_view(), name='like-post'),
    path('posts/<int:post_id>/unlike/', UnlikePostAPI.as_view(), name='unlike-post'),

    # Connection routes
    path('connections/send/<int:user_id>/', SendConnectionRequestAPI.as_view(), name='send-connection'),
    path('connections/incoming/', IncomingRequestsAPI.as_view(), name='incoming-requests'),
    path('connections/accept/<int:user_id>/', AcceptConnectionAPI.as_view(), name='accept-connection'),

    # Recommendation route
    path('recommendations/', RecommendedUsersAPI.as_view(), name='user-recommendations'),
]


