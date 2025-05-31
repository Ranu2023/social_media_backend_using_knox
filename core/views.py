from rest_framework import generics, permissions, status
from rest_framework.response import Response
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
from django.contrib.auth import login
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .models import Post, Like, Connection
from .serializers import RegisterSerializer, UserSerializer, PostSerializer, ConnectionSerializer


# ------------------ Registration API ------------------

class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user)
        return Response({
            "user": UserSerializer(user).data,
            "token": AuthToken.objects.create(user)[1]
        }, status=status.HTTP_201_CREATED)


# ------------------ Login API ------------------

class CustomLoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(CustomLoginAPI, self).post(request, format=None)


# ------------------ Posts ------------------

class PostCreateAPI(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostListAPI(generics.ListAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer


# ------------------ Likes ------------------

class LikePostAPI(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            return Response({'message': 'Already liked.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Post liked'}, status=status.HTTP_200_OK)


class UnlikePostAPI(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        try:
            like = Like.objects.get(user=request.user, post_id=post_id)
            like.delete()
            return Response({'message': 'Post unliked'}, status=status.HTTP_200_OK)
        except Like.DoesNotExist:
            return Response({'message': 'Not liked yet'}, status=status.HTTP_400_BAD_REQUEST)


# ------------------ Connections ------------------

class SendConnectionRequestAPI(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        to_user = get_object_or_404(User, id=user_id)
        if Connection.objects.filter(from_user=request.user, to_user=to_user).exists():
            return Response({'message': 'Request already sent'}, status=status.HTTP_400_BAD_REQUEST)
        Connection.objects.create(from_user=request.user, to_user=to_user)
        return Response({'message': 'Request sent'}, status=status.HTTP_200_OK)


class IncomingRequestsAPI(generics.ListAPIView):
    serializer_class = ConnectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Connection.objects.filter(to_user=self.request.user, status='pending')


class AcceptConnectionAPI(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        conn = get_object_or_404(Connection, to_user=request.user, from_user_id=user_id)
        conn.status = 'accepted'
        conn.save()
        return Response({'message': 'Request accepted'}, status=status.HTTP_200_OK)


# ------------------ Recommendations ------------------

class RecommendedUsersAPI(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        accepted_conns = Connection.objects.filter(from_user=user, status='accepted').values_list('to_user', flat=True)
        mutuals = Connection.objects.filter(from_user__in=accepted_conns, status='accepted') \
                                    .exclude(to_user=user) \
                                    .values_list('to_user', flat=True)
        recommendations = User.objects.filter(id__in=mutuals).exclude(id__in=accepted_conns).exclude(id=user.id).distinct()
        return Response(UserSerializer(recommendations, many=True).data)
