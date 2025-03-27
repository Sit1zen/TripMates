from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Post
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io


class UserRegistrationTest(TestCase):
    def test_register_user(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TestPassword123',
            'password2': 'TestPassword123',
            'gender': 'male', 
        })
        # Check redirect to login
        self.assertRedirects(response, reverse('login'))
        # Check user was created
        self.assertTrue(User.objects.filter(username='testuser').exists())


class UserLoginTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='secret')

    def test_login_success(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'secret'
        })
        self.assertRedirects(response, reverse('index'))  
        self.assertTrue('_auth_user_id' in self.client.session)


class PostCreationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='poster', password='password')
        self.client.login(username='poster', password='password')

    def test_create_post(self):
        
        image_io = io.BytesIO()
        image = Image.new('RGB', (100, 100), color='blue')
        image.save(image_io, 'JPEG')
        image_io.seek(0)

        uploaded_image = SimpleUploadedFile(
            name='test.jpg',
            content=image_io.read(),
            content_type='image/jpeg'
        )

        response = self.client.post(reverse('create_post'), {
            'caption': 'My test post',
            'image': uploaded_image,
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), 1)
        self.assertContains(response, 'My test post')


