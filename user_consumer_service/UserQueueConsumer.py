import sys
import pika
import signal
import logging


class UserQueueConsumer(object):


    def __init__(self, consumer_callback, exchange, **kwargs):
        self.connection = None
        self.channel = None
        self.closing = False
        self.consumer_tag = None
        self.logger = logging.getLogger(__name__)
        self.consumer_callback = consumer_callback
        self.exchange = exchange
        self.parse_input_args(kwargs)

    def parse_input_args(self, kwargs):
        self.user = kwargs.get('user', 'guest')
        self.password = kwargs.get('password', 'guest')
        self.host = kwargs.get('host', '127.0.0.1')
        self.port = kwargs.get('port', 5672)
        self.virtual_host = kwargs.get('virtual_host', '/')
        self.ssl = kwargs.get('ssl', False)
        self.exchange_type = kwargs.get('exchange_type')
        self.queue = kwargs.get('queue', 'add')
        self.binding_keys = kwargs.get('binding_keys', ['add'])
        self.queue_exclusive = kwargs.get('queue_exclusive', False)
        self.queue_durable = kwargs.get('queue_durable', True)
        self.no_ack = kwargs.get('no_ack', False)
        self.safe_stop = kwargs.get('safe_stop', True)

        # if queue name is empty string server will choose a random queue name
        # and we want this queue to be deleted when connection closes, hence
        # setting queue_exclusive True
        if not self.queue:
            self.queue_exclusive = True

    def __create_connection(self):
        self.credentials = pika.PlainCredentials(self.user, self.password)
        self.parameters = pika.ConnectionParameters(host=self.host, port=self.port, virtual_host=self.virtual_host, credentials=self.credentials, ssl=self.ssl)
        return pika.SelectConnection(parameters=self.parameters,on_open_callback=self.__on_connection_open,stop_ioloop_on_close=False)

    def __on_connection_open(self, unused_connection):
        self.logger.info('Connection opened')
        self.__open_channel()

    def __open_channel(self):
        self.logger.info('Creating a new channel')
        self.connection.channel(on_open_callback=self.__on_channel_open)

    def __on_channel_open(self, channel):
        self.logger.info('Channel opened')
        self.channel = channel
        if self.exchange_type:
            self.__setup_exchange(self.exchange)
        else:
            self.logger.info(
                'Skipped exchange setup assuming that exchange already exists')
            self.__setup_queue(self.queue)

    def __setup_exchange(self, exchange_name):
        self.logger.info('Declaring exchange %s', exchange_name)
        self.channel.exchange_declare(self.__on_exchange_declareok,
                                       exchange_name,
                                       self.exchange_type)

    def __on_exchange_declareok(self, unused_frame):
        self.logger.info('Exchange declared')
        self.__setup_queue(self.queue)

    def __setup_queue(self, queue_name):
        if queue_name == '':
            self.logger.info('Declaring queue with server defined queue name')
        else:
            self.logger.info('Declaring queue %s', queue_name)
        self.channel.queue_declare(self.__on_queue_declareok, queue=queue_name,
                                    durable=self.queue_durable, exclusive=self.queue_exclusive)

    def __on_queue_declareok(self, method_frame):
        if self.queue == '':
            self.logger.info('Binding %s to server defined queue with %s',
                              self.exchange, ','.join(self.binding_keys))
        else:
            self.logger.info('Binding %s to %s with %s',
                              self.exchange, self.queue, ','.join(self.binding_keys))
        self.keys_bound_to_queue = 0
        for binding_key in self.binding_keys:
            self.channel.queue_bind(self.__on_bindok, self.queue,
                                     self.exchange, binding_key)

    def __on_bindok(self, unused_frame):
        self.keys_bound_to_queue += 1
        if self.keys_bound_to_queue == len(self.binding_keys):
            self.logger.info('Queue bound')
            self.start_consuming()

    def start_consuming(self):
        self.logger.info('Issuing consumer related RPC commands')
        self.consumer_tag = self.channel.basic_consume(self.__on_message,
                                                         self.queue)

    def __on_message(self, unused_channel, basic_deliver, properties, body):
        self.logger.debug('Received message # %s from %s',
                           basic_deliver.delivery_tag, properties.app_id)
        self.logger.debug('Message Received: %s', body)
        self.consumer_callback(unused_channel, basic_deliver, properties, body)
        if not self.no_ack:
            self.__acknowledge_message(basic_deliver.delivery_tag)

    def __acknowledge_message(self, delivery_tag):
        self.logger.debug('Acknowledging message %s', delivery_tag)
        self.channel.basic_ack(delivery_tag)

    def __stop_consuming(self):
        if self.channel:
            self.logger.info('Sending a Basic.Cancel RPC command to RabbitMQ')
            self.channel.basic_cancel(self.__on_cancelok, self.consumer_tag)

    def __on_cancelok(self, unused_frame):
        self.logger.info(
            'RabbitMQ acknowledged the cancellation of the consumer')
        self.__close_channel()

    def __close_channel(self):
        self.logger.info('Closing the channel')
        self.channel.close()

    def run(self):
        if self.safe_stop:
            signal.signal(signal.SIGTERM, self.__signal_term_handler)
        self.connection = self.__create_connection()
        self.connection.ioloop.start()

    def __signal_term_handler(self, signal, frame):
        try:
            self.stop()
        except Exception as e:
            LOGGER.error(
                "Could not gracefully stop connection on raised signal: " + str(e))
        sys.exit(0)

    def stop(self):
        self.logger.info('Stopping')
        self.closing = True
        self.__stop_consuming()
        self.connection.ioloop.stop()
        self.logger.info('Stopped')

    def close_connection(self):
        self.logger.info('Closing connection')
        self.connection.close()