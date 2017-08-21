import unittest
from django.test import TestCase
from user_service.util.UserUtil import UserUtil
from user_service.payloads.UserPayload import UserPayload
from user_service.repository.Model import Model

class TestAccountKeyClient(TestCase):

	def setUp(self):
		self.user_util = UserUtil()
		self.model = Model()

	def test_add_users(self):
		result = False
		email = 'sample1@example1.com'
		password = 'Hello1234'
		phone_number = '1234967891'
		user_payload = UserPayload()
		user_payload.email = email
		user_payload.password = password
		user_payload.phone_number = phone_number
		key = self.user_util.create_key(user_payload)
		user_payload.key = key
		id = self.model.add_users(user_payload)
		if(isinstance(id, int)):
			result=True
		self.assertEquals(result, True)

	def test_get_users(self):
		result = False
		users = self.model.get_users()
		if(isinstance(users, list)):
			result=True
		self.assertEquals(result, True)

	def test_get_users(self):
		result = False
		users = self.model.get_users_by_query_str('age 32')
		if(isinstance(users, list)):
			result = True
		self.assertEquals(result, True)

	def test_update_users(self):
		result = True
		self.model.update_user(1, 'account_key')
		self.assertEquals(result, True)




