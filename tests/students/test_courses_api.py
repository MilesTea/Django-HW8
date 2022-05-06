import random
from pprint import pprint
import pytest
from django.contrib.auth.models import User
from model_bakery import baker
from rest_framework.test import APIClient
import ast
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
    response = client.get(api_url + f'courses/{course[0].id}/')
    assert response.status_code == 200

    data = response.json()
    assert data['name'] == course[0].name


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
    course = course_factory(_quantity=max_courses)
    required_course = course[random.randint(0, max_courses - 1)]

    response = client.get(api_url + 'courses/', data={'id': required_course.id})
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]['id'] == required_course.id


@pytest.mark.django_db
def test_courses_filter_name(client, user, course_factory):
    course = course_factory(_quantity=max_courses)
    required_course = course[random.randint(0, max_courses - 1)]

    response = client.get(api_url + 'courses/', data={'name': required_course.name})
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == required_course.name


@pytest.mark.django_db
def test_courses_post(client, user):
    count = Course.objects.count()
    course_raw_data = {'name': 'test_course'}
    assert client.post(api_url + 'courses/', data=course_raw_data, format='json').status_code == 201
    assert Course.objects.count() == count + 1


@pytest.mark.django_db
def test_courses_patch(client, user, course_factory):
    count = Course.objects.count()
    course_raw_data = {'name': 'test_course'}
    course_new_raw_data = {'name': 'redacted_course'}

    # Создание объекта
    course_required = course_factory(_quantity=1, name=course_raw_data['name'])

    # Изменение объекта
    new_response = client.patch(api_url + f'courses/{course_required[0].id}/', data=course_new_raw_data, format='json')
    assert new_response.status_code == 200
    new_course = ast.literal_eval(new_response.content.decode('utf-8'))

    assert new_course['name'] == course_new_raw_data['name']


@pytest.mark.django_db
def test_courses_delete(client, user, course_factory):
    count = Course.objects.count()
    course_raw_data = {'name': 'test_course'}

    # Создание объекта
    course_required = course_factory(_quantity=1, name=course_raw_data['name'])

    # Удаление объекта
    assert client.delete(api_url + f'courses/{course_required[0].id}/').status_code == 204
    assert Course.objects.count() == count