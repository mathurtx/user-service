import unittest
from django.test import TestCase
from user_consumer_service.AccountKeyClient import AccountKeyClient
from user_service.util.UserUtil import UserUtil
from user_service.payloads.UserPayload import UserPayload

class TestAccountKeyClient(TestCase):

	def setUp(self):
		self.akc = AccountKeyClient()
		self.user_util = UserUtil()

	def test_get_account_key(self):
		result = False
		email = 'sample@example.com'
		password = 'Hello1234'
		phone_number = '1234567891'
		user_payload = UserPayload()
		user_payload.email = email
		user_payload.password = password
		user_payload.phone_number = phone_number
		key = self.user_util.create_key(user_payload)
		account_key = self.akc.get_account_key(key, email)
		if account_key is not None:
			result = True
		self.assertEquals(result, True)

		
