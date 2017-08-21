import requests
import json
import logging

class AccountKeyClient:

	ACCOUNT_KEY_URL = "https://account-key-service.herokuapp.com/v1/account"

	def __init__(self):
		self.logger = logging.getLogger(__name__)

	def get_account_key(self, key, email):
		try:
			payload = {}
			headers = {"Content-Type":"application/json"}
			payload['email'] = email
			payload['key'] = key
			data = json.dumps(payload)
			self.logger.info("Sending request to account key service " + data)
			response = requests.post(AccountKeyClient.ACCOUNT_KEY_URL, data=data, headers=headers)
			self.logger.info("Response from account key service " + str(response.json()))
			return response.json()['account_key']
		except Exception as e:
			self.logger.error("Error at account key client" + str(e))
			raise e
