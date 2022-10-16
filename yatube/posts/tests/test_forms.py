from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )
        cls.post1 = Post.objects.create(
            author=cls.user,
            text='отредактированный текст поста',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Test Valid form saves a post in DB"""
        posts_count = Post.objects.count()
        form_data = {'text': 'test',
                     'group': self.group.pk}
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': self.post.author})
                             )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(text='Тестовый пост').exists())
        self.assertTrue(Post.objects.filter(author=self.post.author).exists())
        self.assertTrue(Post.objects.filter(group=self.post.pk).exists())

    def test_edit_post(self):
        """Test post save after edit"""
        form_data = {'text': 'Другой текст',
                     'group': 'pink'}
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
        )
        post = Post.objects.get(pk=self.post.pk)
        self.assertNotEqual(
            post.text,
            form_data['text'])
        self.assertNotEqual(
            post.group.pk,
            form_data['group'])
        self.assertEqual(response.status_code, 200)
