# apps/oAuth/tests.py

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class AuthTests(APITestCase):

    def test_register_student(self):
        url = reverse('register')
        data = {
            "username": "student1",
            "email": "student1@example.com",
            "password": "password123",
            "password_confirmation": "password123",
            "role": "student",
            "student_id": "S123456",
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        user = CustomUser.objects.get(email="student1@example.com")
        self.assertEqual(user.role, "student")
        self.assertEqual(user.student_id, "S123456")
        self.assertIsNone(user.teacher_id)

    def test_register_teacher(self):
        url = reverse('register')
        data = {
            "username": "teacher1",
            "email": "teacher1@example.com",
            "password": "password123",
            "password_confirmation": "password123",
            "role": "teacher",
            "teacher_id": "T654321",
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        user = CustomUser.objects.get(email="teacher1@example.com")
        self.assertEqual(user.role, "teacher")
        self.assertEqual(user.teacher_id, "T654321")
        self.assertIsNone(user.student_id)

    def test_login(self):
        # 首先创建一个用户
        user = CustomUser.objects.create_user(username="user1", email="user1@example.com", password="password123")
        user.role = 'student'
        user.student_id = "S123456"
        user.save()

        url = reverse('login')
        data = {
            "email": "user1@example.com",
            "password": "password123",
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        url = reverse('login')
        data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword",
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unique_student_id(self):
        # 创建第一个学生用户
        CustomUser.objects.create_user(username="student1", email="student1@example.com", password="password123", role="student", student_id="S123456")
        # 尝试创建第二个学生用户，学号重复
        url = reverse('register')
        data = {
            "username": "student2",
            "email": "student2@example.com",
            "password": "password123",
            "password_confirmation": "password123",
            "role": "student",
            "student_id": "S123456",  # 重复学号
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('student_id', response.data)

    def test_unique_teacher_id(self):
        # 创建第一个教师用户
        CustomUser.objects.create_user(username="teacher1", email="teacher1@example.com", password="password123", role="teacher", teacher_id="T654321")
        # 尝试创建第二个教师用户，工号重复
        url = reverse('register')
        data = {
            "username": "teacher2",
            "email": "teacher2@example.com",
            "password": "password123",
            "password_confirmation": "password123",
            "role": "teacher",
            "teacher_id": "T654321",  # 重复工号
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('teacher_id', response.data)

    def test_logout(self):
        # 创建并登录一个用户
        user = CustomUser.objects.create_user(username="user2", email="user2@example.com", password="password123")
        user.role = 'teacher'
        user.teacher_id = "T654321"
        user.save()
        url = reverse('login')
        data = {
            "email": "user2@example.com",
            "password": "password123",
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        refresh_token = response.data['refresh']

        # 注销用户
        logout_url = reverse('logout')
        logout_data = {
            "refresh": refresh_token,
        }
        logout_response = self.client.post(logout_url, logout_data, format='json')
        self.assertEqual(logout_response.status_code, status.HTTP_205_RESET_CONTENT)
