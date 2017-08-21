import hashlib
import uuid
import logging

class UserUtil(object):

	REQUIRED_FIELDS = ['email', 'password', 'phone_number']

	def __init__(self):
		self.salt = uuid.uuid4().hex
		logging.basicConfig(filename='UserService.log',level=logging.INFO)
		self.logger = logging.getLogger(__name__)

	def check_data(self,data):
		try:
			self.logger.info(str(data))
			if any(value not in data.keys() for value in UserUtil.REQUIRED_FIELDS):
				return False
			if not self.check_email(data['email']):
					return False
			if not self.check_phone_number(data['phone_number']):
					return False
			return True
		except ValueError as e:
			self.logger.error(str(e))
			raise e

	def create_key(self, user_payload):
		try:
			string_key = user_payload.email + user_payload.phone_number  + user_payload.password
			return hashlib.sha224(string_key.encode('utf-8')).hexdigest()
		except ValueError as e:
			raise e

	def encrypt_password(self, password):
		try:
			return hashlib.sha512(password.encode('utf-8') + self.salt.encode('utf-8')).hexdigest()
		except ValueError as e:
			raise e

	def check_email(self, email):
		if '@' in email:
			return True
		return False

	def check_phone_number(self, phone_number):
		if not phone_number.isdigit():
			return False
		if len(phone_number) > 10:
			return False
		return True

