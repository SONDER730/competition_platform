# apps/oAuth/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

CustomUser = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"detail": "注册成功，请登录。"}, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data['password']
        role = serializer.validated_data['role']

        if role == 'student':
            student_id = serializer.validated_data.get('student_id')
            try:
                user = CustomUser.objects.get(role='student', student_id=student_id)
            except CustomUser.DoesNotExist:
                return Response({"detail": "学号或密码不正确。"}, status=status.HTTP_401_UNAUTHORIZED)
        elif role == 'teacher':
            teacher_id = serializer.validated_data.get('teacher_id')
            try:
                user = CustomUser.objects.get(role='teacher', teacher_id=teacher_id)
            except CustomUser.DoesNotExist:
                return Response({"detail": "工号或密码不正确。"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"detail": "无效的身份选择。"}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(password):
            return Response({"detail": "密码不正确。"}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"detail": "缺少刷新令牌。"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            print(f"Received refresh token: {refresh_token}")  # 调试日志
            token = RefreshToken(refresh_token)
            token.blacklist()
            print("Refresh token has been blacklisted.")  # 调试日志
            return Response(
                {"detail": "注销成功。"},
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            print(f"Error during logout: {str(e)}")  # 调试日志
            return Response(
                {"detail": "无效的刷新令牌。"},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_object(self):
        return self.request.user