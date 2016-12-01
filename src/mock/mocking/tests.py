from django.test import TestCase

from django.test import TestCase, Client
from django.contrib.auth.models import User
from mocking.models import *
import json


# Create your tests here.


class UserExtendTest(TestCase):
    client = Client()

    def test_register(self):
        request_object = {
            'username': 'zhehuiz',
            'first_name': 'zhehui',
            'last_name': 'zhou',
            'email': 'grayy921013@gmail.com',
            'pwd': '123456',
            'pwd2': '123456',
        }

        self.assertTrue(User.objects.all().count() == 0)
        self.client.post('/mocking/register', request_object)
        self.assertTrue(User.objects.all().count() == 1)

    def test_login(self):
        response = self.client.get("/mocking/get_interview_list")
        self.assertNotEqual(response.status_code, 200)
        self.test_register()
        request_object = {
            'username': 'zhehuiz',
            'password': '123456',
        }
        self.client.post("/mocking/login", request_object)
        response = self.client.get("/mocking/get_interview_list")
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        self.test_login()
        self.client.get("/mocking/logout")
        response = self.client.get("/mocking/get_interview_list")
        self.assertNotEqual(response.status_code, 200)