import sys
import pika
import signal
import logging

class UserQueuePublisher(object):
    

    def __init__(self, exchange, **kwargs):
        self.connection = None
        self.messages = {}
        self.message_number = 0
        self.channel_closing = False
        self.connection_closing = False
        self.channel = None
        self.logger = logging.getLogger(__name__)
        self.exchange = exchange
        self.__extract_input_args(kwargs)
        self.__create_connection()
        self.run()

    def __extract_input_args(self, kwargs):
        self.user = kwargs.get('user', 'guest')
        self.password = kwargs.get('password', 'guest')
        self.host = kwargs.get('host', '127.0.0.1')
        self.port = kwargs.get('port', 5672)
        self.virtual_host = kwargs.get('virtual_host', '/')
        self.ssl = kwargs.get('ssl', False)
        self.exchange_type = kwargs.get('exchange_type', 'topic')
        self.routing_key = kwargs.get('routing_key', 'add')
        self.exchange_durable = kwargs.get('exchange_durable', True)
        self.exchange_auto_delete = kwargs.get('exchange_auto_delete', False)
        self.exchange_internal = kwargs.get('exchange_internal', False)
        self.delivery_confirmation = kwargs.get('delivery_confirmation', True)
        self.nack_callback = kwargs.get('nack_callback')
        self.safe_stop = kwargs.get('safe_stop', True)
        self.reconnect_time = kwargs.get('reconnect_time', 5)

    def __create_connection(self):
        self.credentials = pika.PlainCredentials(self.user, self.password)
        self.parameters = pika.ConnectionParameters(host=self.host, port=self.port, virtual_host=self.virtual_host, credentials=self.credentials, ssl=self.ssl)
        self.connection_closing = False
        self.logger.info('Connecting to %s', self.parameters)
        if self.connection is None:
            try:
                self.connection = pika.SelectConnection(parameters=self.parameters,
                                                   on_open_callback=self.__on_connection_open, on_close_callback=self.__on_connection_closed,
                                                   stop_ioloop_on_close=False)
            except Exception as e:
                self.logger.error(e)
                raise e

    def __on_connection_open(self, unused_connection):
        self.logger.info('Connection opened')
        self.__openchannel()

    def __on_connection_closed(self, connection, reply_code, reply_text):
        self.channel = None
        if self.connection_closing:
            self.logger.info('Connection was closed: (%s) %s',
                              reply_code, reply_text)
            self.connection.ioloop.stop()
        else:
            self.logger.warning('Connection closed, reopening in %d seconds: (%s) %s',
                                 self.reconnect_time, reply_code, reply_text)
            self.connection.add_timeout(self.reconnect_time, self.__reconnect)

    def __reconnect(self):
        unpublished_messages = self.messages
        self.__reset_messages()

        # This is the old connection IOLoop instance, stop its ioloop
        self.connection.ioloop.stop()

        # Create a new connection
        self.__create_connection()

        # There is now a new connection
        self.run()

        # Publishing if messages were unpublished before closing the connection
        if unpublished_messages:
            self.logger.info("Publishing Messages left on reconnection")
            for message in unpublished_messages.values():
                self.publish_message(
                    message['message'], message['routing_key'])

    def __reset_messages(self):
        self.messages = {}
        self.message_number = 0

    def __openchannel(self):
        self.logger.info('Creating a new channel')
        self.channel_closing = False
        self.connection.channel(on_open_callback=self.__onchannel_open)

    def __onchannel_open(self, channel):
        self.logger.info('Channel opened')
        self.channel = channel
        self.__setup_exchange(self.exchange)

    def __setup_exchange(self, exchange_name):
        self.logger.info('Declaring exchange %s', exchange_name)
        self.channel.exchange_declare(self.__on_exchange_declareok, exchange_name,
                                       self.exchange_type, durable=self.exchange_durable,
                                       auto_delete=self.exchange_auto_delete,
                                       internal=self.exchange_internal)

    def __on_exchange_declareok(self, unused_frame):
        """Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.
        :param pika.Frame.Method unused_frame: Exchange.DeclareOk response frame
        """
        self.logger.info('Exchange declared')
        self.__start_publishing()

    def __start_publishing(self):
        self.logger.info('Issuing consumer related RPC commands')
        if self.delivery_confirmation:
            self.__enable_delivery_confirmations()
        else:
            self.connection.ioloop.stop()

    def __enable_delivery_confirmations(self):
        self.logger.info('Issuing Confirm.Select RPC command')
        self.channel.confirm_delivery(self.__on_delivery_confirmation)
        self.connection.ioloop.stop()

    def __on_delivery_confirmation(self, method_frame):
        confirmation_type = method_frame.method.NAME.split('.')[1].lower()
        message_num = method_frame.method.delivery_tag
        if confirmation_type == 'ack':
            self.logger.info('Message %i published successfully',
                              message_num)
            self.logger.debug('The message published: %s',
                               self.messages[message_num]['message'])
        if confirmation_type == 'nack':
            self.logger.error('The message %i failed to publish: %s',
                               message_num, self.messages[message_num]['message'])
            if self.nack_callback:
                self.nack_callback(self.messages[message_num]['message'])
        del self.messages[message_num]
        self.connection.ioloop.stop()

    def publish_message(self, message):
        if self.channel.is_open:
            self.channel.basic_publish(self.exchange, self.routing_key, message, properties=pika.BasicProperties(
                delivery_mode=2, 
            ))
        else:
            self.logger.error("Channel not open. Message %s couldn't be published. "
                               "Will try to publish message again if channel reopens", message)
            return
        self.message_number += 1
        self.messages[self.message_number] = {
            'message': message, 'routing_key': self.routing_key}
        self.logger.debug('Publishing message # %i', self.message_number)

        if self.delivery_confirmation:
            self.connection.ioloop.start()

    def __closechannel(self):
        self.logger.info('Closing the channel')
        if self.channel:
            self.channel.close()

    def run(self, **kwargs):
        self.connection.ioloop.start()

    def __signal_term_handler(self, signal, frame):
        try:
            self.stop_connection()
        except Exception as e:
            self.logger.error(
                "Could not gracefully stop connection on raised signal: " + str(e))
        sys.exit(0)

    def stop(self):
        self.channel_closing = True
        self.__closechannel()
        self.connection.ioloop.start()

    def stop_connection(self):
        self.connection_closing = True
        self.logger.info('Closing connection')
        self.stop()
        self.connection.close()
        self.connection.ioloop.start()
