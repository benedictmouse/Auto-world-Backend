from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import (
    UserRegistrationSerializer, 
    UserDetailSerializer,
    UserListSerializer,
    ApproveUserSerializer,
    PromoteToAdminSerializer
)
from .permissions import IsAdmin

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    Worker self-registration endpoint
    POST: Register new worker (pending approval)
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            "message": "Registration successful. Please wait for admin approval.",
            "user": UserDetailSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class LoginView(views.APIView):
    """
    Login endpoint - returns JWT tokens
    POST: Login with email and password
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {"error": "Please provide both email and password"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.check_password(password):
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Check if user is approved (workers need approval, admins don't)
        if not user.is_staff and not user.is_approved:
            return Response(
                {"error": "Your account is pending approval. Please wait for admin to approve."},
                status=status.HTTP_403_FORBIDDEN
            )

        if not user.is_active:
            return Response(
                {"error": "Account is disabled"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Login successful",
            "user": UserDetailSerializer(user).data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }
        }, status=status.HTTP_200_OK)


class LogoutView(views.APIView):
    """
    Logout endpoint - blacklist refresh token
    POST: Logout user
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response(
                {"message": "Logout successful"},
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception:
            return Response(
                {"error": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST
            )


class PendingWorkersView(generics.ListAPIView):
    """
    List all pending workers (for admin approval)
    GET: List pending workers
    """
    permission_classes = [IsAdmin]
    serializer_class = UserListSerializer

    def get_queryset(self):
        return User.objects.filter(is_approved=False, is_staff=False).order_by('-date_joined')


class ApproveWorkerView(views.APIView):
    """
    Approve or reject worker
    POST: Approve/reject worker
    """
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = ApproveUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data['user_id']
        approve = serializer.validated_data['approve']

        try:
            user = User.objects.get(id=user_id)
            
            if approve:
                user.is_approved = True
                user.save()
                return Response({
                    "message": f"Worker {user.email} has been approved",
                    "user": UserDetailSerializer(user).data
                }, status=status.HTTP_200_OK)
            else:
                # Reject - delete the user
                email = user.email
                user.delete()
                return Response({
                    "message": f"Worker {email} has been rejected and removed"
                }, status=status.HTTP_200_OK)
                
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class PromoteToAdminView(views.APIView):
    """
    Promote approved worker to admin
    POST: Promote worker to admin
    """
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = PromoteToAdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data['user_id']

        try:
            user = User.objects.get(id=user_id)
            user.is_staff = True
            user.save()
            
            return Response({
                "message": f"{user.email} has been promoted to admin",
                "user": UserDetailSerializer(user).data
            }, status=status.HTTP_200_OK)
                
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class AllUsersView(generics.ListAPIView):
    """
    List all users (admin only)
    GET: List all users
    """
    permission_classes = [IsAdmin]
    serializer_class = UserListSerializer
    queryset = User.objects.all().order_by('-date_joined')


class CurrentUserView(generics.RetrieveAPIView):
    """
    Get current authenticated user details
    GET: Current user info
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailSerializer

    def get_object(self):
        return self.request.user