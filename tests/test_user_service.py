import unittest
from rest_framework.test import APITestCase
from rest_framework import status
from user_service.util.UserUtil import UserUtil
from user_service.payloads.UserPayload import UserPayload
from user_service.service.UserService import UserService

class TestUserService(APITestCase):

	def setUp(self):
		self.user_service = UserService()
		data = {}
		data['email'] = "sample2@example.com"
		data['phone_number'] = "8787879787"
		data['password'] = "Hello123"
		data['metadata'] = "This is a sample request"
		self.data = data

	def test_can_add_users(self):
		response = self.client.post('http://127.0.0.1/v1/users', self.data, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

	def test_no_email_add_users(self):
		data = {}
		data['password'] = "Hello123"
		data['phone_number'] = "8787878787"
		data['metadata'] = "This is a sample request"
		response = self.client.post('http://127.0.0.1/v1/users', data, format='json')
		self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

	def test_no_password_add_users(self):
		data = {}
		data['email'] = "sample@example.com"
		data['phone_number'] = "8787878787"
		data['metadata'] = "This is a sample request"
		response = self.client.post('http://127.0.0.1/v1/users', data, format='json')
		self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

	def test_get_users(self):
		response = self.client.get('http://127.0.0.1/v1/users')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_no_phone_number(self):
		data = {}
		data['email'] = "sample2@example.com"
		data['password'] = "Hello123"
		data['metadata'] = "This is a sample request"
		response = self.client.post('http://127.0.0.1/v1/users', data, format='json')
		self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
