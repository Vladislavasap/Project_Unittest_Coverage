from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_posts_group_slug_exists(self):
        """Страница group/<slug:slug>/ доступна любому пользователю."""
        response = self.guest_client.get('/group/test/')
        self.assertEqual(response.status_code, 200)

    def test_posts_profile_exists(self):
        """Страница profile/<str:username>/ доступна любому пользователю."""
        response = self.guest_client.get('/profile/auth/')
        self.assertEqual(response.status_code, 200)

    def test_posts_post_id_exists(self):
        """Страница posts/<int:post_id>/ доступна любому пользователю."""
        response = self.guest_client.get('/posts/1/')
        self.assertEqual(response.status_code, 200)

    def test_posts_unexisting_page_exists(self):
        """Страница unexisting_page доступна любому пользователю."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_posts_create_exists(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_posts_edit_exists(self):
        """Страница /edit/ доступна только автору."""
        response = self.authorized_client.get(f'/posts/{self.post.pk}/edit/',
                                              follow=True)
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{PostsURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_create_url_template(self):
        """Страница /create/ использует верный шаблон."""
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_edit_url_template(self):
        """Страница /...edit/ использует верный шаблон."""
        response = self.authorized_client.get(f'/posts/{self.post.pk}/edit/')
        self.assertTemplateUsed(response, 'posts/create_post.html')