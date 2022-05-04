import random
from pprint import pprint
import pytest
from django.contrib.auth.models import User
from model_bakery import baker
from rest_framework.test import APIClient

from students.models import Course, Student

api_url = '/api/v1/'
max_courses = 10


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user('admin')


@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)

    return factory


@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)

    return factory


@pytest.mark.django_db
def test_courses_get_one(client, user, course_factory):
    course = course_factory(_quantity=1)
    response = client.get(api_url + 'courses/')
    assert response.status_code == 200

    data = response.json()
    for i, data_course in enumerate(data):
        assert data_course['name'] == course[i].name


@pytest.mark.django_db
def test_courses_get_many(client, user, course_factory):
    course = course_factory(_quantity=max_courses)
    response = client.get(api_url + 'courses/')
    assert response.status_code == 200
    data = response.json()

    for i, data_course in enumerate(data):
        assert data_course['name'] == course[i].name


@pytest.mark.django_db
def test_courses_filter_id(client, user, course_factory):
    course_id = random.randint(1, max_courses)
    course = course_factory(_quantity=max_courses)

    response = client.get(api_url + 'courses/', data={'id': course_id})
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]['id'] == course[course_id-1].id


@pytest.mark.django_db
def test_courses_filter_name(client, user, course_factory):
    course_id = random.randint(1, max_courses)
    course = course_factory(_quantity=max_courses)

    response = client.get(api_url + 'courses/', data={'id': course_id})
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == course[course_id-1].name


@pytest.mark.django_db
def test_courses_post(client, user):
    len_courses = len(client.get(api_url + 'courses/').json())
    course_data = {'name': 'test_course'}
    assert client.post(api_url + 'courses/', data=course_data, format='json').status_code == 201

    response = client.get(api_url + 'courses/')
    assert response.status_code == 200

    data = response.json()
    assert len(data) - 1 == len_courses


@pytest.mark.django_db
def test_courses_patch(client, user):
    course_data = {'name': 'test_course'}
    assert client.post(api_url + 'courses/', data=course_data, format='json').status_code == 201

    response = client.get(api_url + 'courses/', data=course_data, format='json')
    assert response.status_code == 200

    data = response.json()
    assert data[0]['name'] == course_data['name']

    course_id = data[0]['id']
    new_course_data = {'name': 'redacted_course'}
    assert client.patch(api_url + f'courses/{course_id}/', data=new_course_data, format='json').status_code == 200

    new_response = client.get(api_url + 'courses/', data=new_course_data, format='json')
    assert new_response.status_code == 200

    new_data = new_response.json()
    assert new_data[0]['name'] == new_course_data['name']


@pytest.mark.django_db
def test_courses_delete(client, user):
    len_courses = len(client.get(api_url + 'courses/').json())
    course_data = {'name': 'test_course'}
    assert client.post(api_url + 'courses/', data=course_data, format='json').status_code == 201

    response = client.get(api_url + 'courses/')
    assert response.status_code == 200

    data = response.json()
    assert len(data) - 1 == len_courses

    course_id = data[0]['id']
    assert client.delete(api_url + f'courses/{course_id}/').status_code == 204

    new_response = client.get(api_url + 'courses/')
    assert new_response.status_code == 200

    new_data = new_response.json()
    assert len(new_data) == len_courses