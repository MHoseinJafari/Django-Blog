from rest_framework.test import APIClient
import pytest
from django.urls import reverse
from accounts.models import User
from blog.models import Blog, Vote, Category

@pytest.fixture
def api_client():
    client = APIClient()
    return client

@pytest.fixture
def common_user():
    user = User.objects.create_user(email='m@gmail.com', password = 'm@1234567', is_verified=True)
    return user

@pytest.fixture
def blog_data():
    Category.objects.create(name = "test")
    data = {
        'title': 'test',
        'content': "test content",
        'category': 1,
        'author':1,
    }
    return data

@pytest.fixture
def blog_obj(common_user):
    category = Category.objects.create(name = "test")
    user = common_user
    data = {
        'title': 'test',
        'content': "test content",
        'category': category,
        'author': user
    }
    blog_data = Blog.objects.create(**data)
    return blog_data 

@pytest.mark.django_db
class TestBlogApi:

    def test_get_blog_response_200_status(self, api_client):
        url = reverse('blog:blog-list')
        response = api_client.get(url)
        assert response.status_code == 200
    
    def test_create_blog_response_201_status(self, api_client, common_user, blog_data):
        url = reverse('blog:blog-list')
        user = common_user
        api_client.force_login(user=user)
        response = api_client.post(url, blog_data, format='json')
        assert response.status_code == 201
        assert Blog.objects.count() == 1
        assert Blog.objects.all()[0].title == 'test'
    
    def test_create_blog_unauthorized_response_401_status(self, api_client, blog_data):
        url = reverse('blog:blog-list')
        response = api_client.post(url, blog_data, format = 'json')
        assert response.status_code == 401
    
    def test_create_blog_not_verified_response_403_status(self, api_client, common_user, blog_data):
        url = reverse('blog:blog-list')
        user = common_user
        user.is_verified = False
        user.save()
        api_client.force_login(user=user)
        response = api_client.post(url, blog_data, format = 'json')
        assert response.status_code == 403
    
    def test_create_blog_no_title_bad_reauest_response_400_status(self, api_client, common_user):
        url = reverse('blog:blog-list')
        user = common_user
        api_client.force_login(user=user)
        data = {
            'content': "test content",
            'category':1,
            'author':1,
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == 400
        assert Blog.objects.count() == 0
    
    def test_put_blog_response_200_status(self, api_client, common_user, blog_obj):
        url = reverse('blog:blog-detail', args=[blog_obj.id])
        data = {
            'title': 'test edited by put',
            'content': "test content with put",
            'category': 1,
            'vote': 4,
        }
        user = common_user
        api_client.force_login(user=user)
        response = api_client.put(url, data, format='json')
        blog = Blog.objects.all()[0]
        assert response.status_code == 200
        assert Blog.objects.count() == 1
        assert blog.title == 'test edited by put'
        assert blog.content == 'test content with put'
        assert blog.rate == 4
        




