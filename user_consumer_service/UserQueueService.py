from UserQueueConsumer import UserQueueConsumer
from AccountKeyClient import AccountKeyClient
import logging, schedule, time, json
from Model import Model

class UserQueueService(object):

	EXCHANGE_NAME = "user"
	SCHEDULE_PERIOD = 30

	def __init__(self):
		logging.basicConfig(filename='UserQueueService.log',level=logging.INFO)
		self.logger = logging.getLogger(__name__)
		self.model = Model()
		self.exchange_name = UserQueueService.EXCHANGE_NAME
		self.account_key_client = AccountKeyClient()
		self.schedule_consumer()

	def add_users(self):
		user_queue = None
		try:
		    self.user_queue = UserQueueConsumer(self.get_account_key, UserQueueService.EXCHANGE_NAME)
		    self.logger.info(self.user_queue.consumer_callback)
		    self.user_queue.run()
		except Exception as e:
			self.logger.error("Error running queue consumer " + str(e))

	def get_account_key(self, unused_channel, basic_deliver, properties, request):
		try:
			json_data = json.loads(request)
			email = json_data['email']
			key = json_data['key']
			id = json_data['id']
			account_key = self.account_key_client.get_account_key(email, key)
			if account_key is None:
				self.logger.error("No value returned from account key service %s %s", email, key)
				raise ValueError("No value retrieved from Account Key Service")
			else:
				self.model.update_user(id, account_key)
			print(account_key)
		except Exception as e:
			self.logger.error("Error with get account key" + str(e))

	def schedule_consumer(self):
		try:
			self.add_users()
			schedule.every(UserQueueService.SCHEDULE_PERIOD).seconds.do(self.add_users)
			while True:
				schedule.run_pending()
		except Exception as e:
			self.logger.error("Error running consumer job " + str(e))
			raise e