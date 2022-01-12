from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from marshmallow.exceptions import ValidationError
import pika
import pymongo
import requests
from requests.models import HTTPError
import sys
import time

from schemas import Timer
import settings

# ----------------------------------------------------------------------------

format = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(stream=sys.stdout, format=format, level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------------


class TimerExecuter:
    def __init__(self):
        self.scheduler = self._start_scheduler()
        self._start_consumer(
            settings.MQ_BROKER_HOST,
            settings.MQ_BROKER_PORT,
            settings.MQ_EXCHANGE,
            settings.MQ_QUEUE_NAME,
            self._add_job,
        )

    def _start_scheduler(self):
        retries = 3
        while retries > 0:
            time.sleep(1)

            try:
                scheduler = BackgroundScheduler(timezone="UTC")
                scheduler.add_jobstore(
                    jobstore="mongodb",
                    collection=settings.MONGO_JOB_SCHEDULER_COLLECTION,
                    host=settings.MONGO_URI,
                )
                scheduler.start()
                logger.info("Started job scheduler")
                retries = 0
            except pymongo.errors.ConnectionFailure as e:
                pass

            retries -= 1

        return scheduler

    def _start_consumer(
        self, broker_host, broker_port, exchange, message_queue, callback
    ):
        retries = 3
        while retries:

            # this is a bit of a hacky solution
            # to make sure the scheduler waits for the rabbitMQ container
            # to be ready before starting the consumer.
            # in production, we would do this in a more fault tolerant
            # fashion via something like health checks.
            time.sleep(10)

            try:
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=broker_host, port=broker_port)
                )

                channel = connection.channel()
                channel.exchange_declare(
                    exchange=exchange, durable=True, exchange_type="topic"
                )
                channel.queue_declare(queue=message_queue, durable=True)
                channel.queue_bind(
                    exchange=exchange, queue=message_queue, routing_key=message_queue
                )
                channel.basic_consume(message_queue, callback)

                retries = 0
                logger.info("Start queue consumer")
                channel.start_consuming()

            except pika.exceptions.AMQPConnectionError as e:
                print("error")
                pass

            retries -= 1

    def _add_job(self, ch, method, properties, body):
        try:
            job = Timer().loads(body)
            run_time = datetime.utcfromtimestamp(job["expiry_time"])
            id = job["id"]
            url = job["url"]
        except ValidationError as e:
            logger.exception(e.messages)
            logger.error("Invalid message format")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        except KeyError as e:
            logger.exception(e)
            logger.error("Key not found")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        logger.debug(f"added URL: {url} ID: {id}")
        self.scheduler.add_job(
            func=send_webhook,
            trigger="date",
            args=[url, id],
            next_run_time=run_time,
            # this notifies the scheduler to always retry the job in the case of a missed job
            # (i.e. in the case of a reboot)
            misfire_grace_time=None,
        )

        ch.basic_ack(delivery_tag=method.delivery_tag)


def send_webhook(url, id):
    logger.debug(f"Executing URL: {url} ID: {id}")
    response = requests.post(f"{url}/{id}")
    try:
        response.raise_for_status()
    except HTTPError as e:
        # we could send a notification to the user here
        # notifying of a failure
        # for now, we shall just log the failure and continue
        logger.exception(f"Webhook failed: {url}/{id}")


if __name__ == "__main__":
    TimerExecuter()
