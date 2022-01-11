import time

import pika

# ----------------------------------------------------------------------------


class MqConnectionError(Exception):
    pass


# ----------------------------------------------------------------------------


class MessageQueueClient:
    def __init__(self, broker_host, broker_port):

        self.broker_host = broker_host
        self.broker_port = broker_port

        self.connection = None
        retries = 3

        while retries:
            try:
                self._connect()
                retries = 0
            except pika.exceptions.AMQPConnectionError as e:
                print("retrying")
                retries -= 1
                time.sleep(3)

        if not self.channel:
            raise MqConnectionError("Could not connect to MQ broker")

    def _connect(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.broker_host, port=self.broker_port)
        )

        self.channel = self.connection.channel()

    def publish(self, queue_name, message):
        if type(message) not in (str, dict):
            raise ValueError("message is not in expected format")

        if self.connection.is_closed:
            self._connect()

        self.channel.basic_publish(
            exchange="timeit", routing_key=queue_name, body=message
        )
