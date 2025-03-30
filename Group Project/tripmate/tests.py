from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Post, UserProfile
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io
import os
from django.core.files import File
from django.conf import settings


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

class ProfileTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='john', password='doe1234')
        UserProfile.objects.create(user=self.user)

    def test_profile_view(self):
        self.client.login(username='john', password='doe1234')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)

class FriendSystemTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='alice', password='password1')
        self.user2 = User.objects.create_user(username='bob', password='password2')
        UserProfile.objects.create(user=self.user1)
        UserProfile.objects.create(user=self.user2)
        self.client.login(username='alice', password='password1')

    def test_add_and_remove_friend(self):
        response_add = self.client.post(reverse('add_friend', args=['bob']))
        self.assertEqual(response_add.status_code, 302)
        self.assertIn(self.user2.userprofile, self.user1.userprofile.friends.all())

        response_remove = self.client.post(reverse('remove_friend', args=['bob']))
        self.assertEqual(response_remove.status_code, 302)
        self.assertNotIn(self.user2.userprofile, self.user1.userprofile.friends.all())

class SearchTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='searcher', password='testpass')
        self.other = User.objects.create_user(username='founduser', password='pass')
        UserProfile.objects.create(user=self.user)
        UserProfile.objects.create(user=self.other)
        self.client.login(username='searcher', password='testpass')

    def test_user_search(self):
        response = self.client.get(reverse('user_search') + '?q=founduser')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'founduser')

    def test_post_feed_filter(self):
        image_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'default-profile.jpg')
        with open(image_path, 'rb') as img:
            uploaded_image = SimpleUploadedFile(
                name='default-profile.jpg',
                content=img.read(),
                content_type='image/jpeg'
            )
            Post.objects.create(user=self.user, caption='Only mine', image=uploaded_image)
            Post.objects.create(user=self.other, caption='Not mine', image=uploaded_image)
        response = self.client.get(reverse('post_feed') + '?mine=1')
        self.assertContains(response, 'Only mine')
        self.assertNotContains(response, 'Not mine')
