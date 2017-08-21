import sqlite3
import logging
import datetime

class Model(object):


	CREATE_USER_TABLE = '''CREATE TABLE IF NOT EXISTS user_table(
						   created_ts TIMESTAMP NOT NULL,
						   id INTEGER PRIMARY KEY,
						   email VARCHAR(200) NOT NULL UNIQUE,
						   phone_number VARCHAR(20) NOT NULL UNIQUE,
						   full_name VARCHAR(200),
						   password VARCHAR(100) NOT NULL,
						   key VARCHAR(100) NOT NULL UNIQUE,
						   account_key VARCHAR(100) UNIQUE,
						   metadata VARCHAR(2000)
						);
						'''
	DROP_USER_TABLES = ''' DROP TABLE IF EXISTS user_table;'''

	GET_USERS = '''SELECT email, phone_number, full_name, key, account_key, metadata
				   FROM user_table ORDER BY created_ts DESC;
				'''

	GET_USERS_BY_NAME = '''SELECT email, phone_number, full_name, key, account_key, metadata
						   FROM user_table WHERE full_name like ?  or email like ?  or metadata like ? ORDER BY created_ts DESC;
						'''

	INSERT_USER_ROW = '''INSERT INTO user_table(created_ts, email, phone_number, full_name, password, key, metadata) 
						 VALUES(?, ?, ?, ?, ?, ?, ?); '''
						 
	UPDATE_USER_ROW = '''UPDATE user_table SET account_key = ? WHERE id = ?;'''

	DB_NAME = '/user.db'

	def __init__(self):
		logging.basicConfig(filename='database.log',level=logging.INFO)
		self.connection = sqlite3.connect(Model.DB_NAME, timeout=5)
		self.logger = logging.getLogger(__name__)
		self.cursor = self.connection.cursor()
		self.__create_tables()

	def __create_tables(self):
		try:
			self.logger.info("Creating user table")
			self.cursor = self.cursor.execute(Model.CREATE_USER_TABLE)
		except sqlite3.Error as e:
			self.logger.error("Error creating user table " + str(e))
			raise e

	def add_users(self, user_payload):
		try:
			created_ts = datetime.datetime.now()
			email = user_payload.email
			phone_number = user_payload.phone_number
			full_name = user_payload.full_name
			password = user_payload.password
			key = user_payload.key
			metadata = user_payload.metadata
			self.cursor.execute(Model.INSERT_USER_ROW, (created_ts, email, phone_number, full_name, password, key, metadata))
			self.connection.commit()
			return self.cursor.lastrowid
		except sqlite3.Error as e:
			self.logger.error("Error adding user to user table " + str(e))
			raise e

	def update_user(self, ID, account_key):
		try:
			self.cursor.execute(Model.UPDATE_USER_ROW, (account_key, ID))
			self.connection.commit()
		except sqlite3.Error as e:
			self.logger.error("Error updating the user record with account key" + str(e))
			raise e

	def get_users(self):
		try:
			self.logger.info("Fetching all users from user table")
			self.cursor = self.cursor.execute(Model.GET_USERS)
			return self.cursor.fetchall()
		except sqlite3.Error as e:
			self.logger.error("Error getting users from user table" + str(e))
			raise e

	def get_users_by_query_str(self, query):
		try:
			self.logger.info("Getting users from user table that matches :" + query)
			self.cursor = self.cursor.execute(Model.GET_USERS_BY_NAME, ('%'+query+'%', '%'+query+'%', '%'+query+'%'))
			return self.cursor.fetchall()
		except sqlite3.Error as e:
			self.logger.error("Error getting users from user table that matches query " + query + str(e))
			raise e

	def __drop_tables(self):
		try:
			self.logger.info("Deleting user table")
			self.cursor = self.cursor.execute(Model.DROP_USER_TABLES)
		except sqlite3.Error as e:
			self.logger.error("Error deleting user table" + str(e))
			raise e
