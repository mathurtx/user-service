import json

class UserPayload(object):
	
	def __init__(self, full_name=None, email=None, phone_number=None, password=None, key=None, account_key=None, metadata=None):
		self._full_name = full_name
		self._email = email
		self._phone_number = phone_number
		self._password = password
		self._key = key
		self._account_key = account_key
		self._metadata = metadata

	@property
	def full_name(self):
		return self._full_name

	@property
	def email(self):
		return self._email

	@property
	def phone_number(self):
		return self._phone_number

	@property
	def password(self):
		return self._password

	@property
	def key(self):
		return self._key

	@property
	def account_key(self):
		return self._account_key

	@property
	def metadata(self):
		return self._metadata

	@email.setter
	def email(self, email):
		if email is None:
			raise ValueError("Email cannot be null")
		self._email = email

	@phone_number.setter
	def phone_number(self, phone_number):
		if phone_number is None:
			raise ValueError("Phone number cannot be null")
		self._phone_number = phone_number

	@password.setter
	def password(self, password):
		if password is None:
			raise ValueError("Password cannot be none")
		self._password = password

	@key.setter
	def key(self, key):
		if key is None:
			raise ValueError("Key cannot be null")
		self._key = key

	@account_key.setter
	def account_key(self, account_key):
		self._account_key = account_key

	@metadata.setter
	def metadata(self, metadata):
		self._metadata = metadata

	@full_name.setter
	def full_name(self, full_name):
		self._full_name = full_name

	def __str__(self):
		return self._email + ' ' + self._phone_number + ' ' + self.password



