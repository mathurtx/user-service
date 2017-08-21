from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from user_service.util.UserUtil import UserUtil
from user_service.connectors.UserQueuePublisher import UserQueuePublisher
from user_service.repository.Model import Model
from user_service.payloads.UserPayload import UserPayload
import logging, json, sqlite3


class UserService(viewsets.ViewSet):

	EXCHANGE_NAME = "user"

	def __init__(self):
		logging.basicConfig(filename='UserService.log',level=logging.INFO)
		self.logger = logging.getLogger(__name__)
		self.user_publisher = UserQueuePublisher(UserService.EXCHANGE_NAME)
		self.user_util = UserUtil()
		self.model = Model()

	def get_users(self, request):
		try:
			self.logger.info("Get all user information " + str(request.data))
			query = request.GET.get('query', '')
			self.logger.debug("Get all users has query param " + query)
			if not query == '': 
				all_users = self.model.get_users_by_query_str(query)
			else:
				all_users = self.model.get_users()
			return Response(all_users)
		except Exception as e:
			self.logger.error("Error occurred in getting all users")
			return Response("Server Error", status=HTTP_503_SERVICE_UNAVAILABLE)

	def add_users(self, request):
		try:
			self.logger.info("Adding user information " + str(request.data))
			if self.user_util.check_data(request.data):
				request_data = json.loads(json.dumps(request.data))
				user_payload = UserPayload(**request_data)
				user_payload.key = self.user_util.create_key(user_payload)
				user_payload.password = self.user_util.encrypt_password(user_payload.password)
				id = self.model.add_users(user_payload)
				request.data['id'] = id
				request.data['key'] = user_payload.key
				self.user_publisher.publish_message(json.dumps(request.data))
				return Response("User record created. The account key may not be accessible instantly.", status=status.HTTP_201_CREATED)
			else:
				content = { "errors": ["Phone number is too long","Email is missing"]}
				return Response(content, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
		except sqlite3.IntegrityError as e:
			return Response("User already exists", status=status.HTTP_406_NOT_ACCEPTABLE)
		except Exception as e:
			self.logger.error("Error occurred in adding users" + str(request.data))
			return Response("Server Error", status=HTTP_503_SERVICE_UNAVAILABLE)

