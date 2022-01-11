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

# ----------------------------------------------------------------------------

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# ----------------------------------------------------------------------------

# def retry_on_exception(callable, exceptions, retries, retry_time, *args, **kwargs):
#     retries_left = retries
#     try:
#         if retries_left:
#             return callable(*args, **kwargs)
#         else:

#     except exceptions:
#         retries_left -= 1
#         time.sleep(retry_time)


class TimerExecuter:
    def __init__(self):
        self.scheduler = self._start_scheduler()
        self._start_consumer("mq", "timers", self._add_job)

    def _start_scheduler(self):
        retries = 3
        while retries > 0:
            try:
                scheduler = BackgroundScheduler(timezone="UTC")
                scheduler.add_jobstore(
                    jobstore="mongodb",
                    collection="timer-jobs",
                    host="mongodb://db:27017",
                )
                scheduler.start()
                retries = 0
            except pymongo.errors.ConnectionFailure as e:
                pass

            retries -= 1
            time.sleep(1)

        return scheduler

    def _start_consumer(self, broker_host, message_queue, callback):
        retries = 3
        while retries:
            time.sleep(10)

            try:
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=broker_host, port=5672)
                )

                channel = connection.channel()
                channel.exchange_declare(
                    exchange="timeit", durable=True, exchange_type="topic"
                )
                channel.queue_declare(queue=message_queue, durable=True)
                channel.queue_bind(
                    exchange="timeit", queue=message_queue, routing_key=message_queue
                )
                channel.basic_consume(message_queue, callback)

                retries = 0
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

        self.scheduler.add_job(
            func=send_webhook,
            trigger="date",
            args=[url, id],
            next_run_time=run_time,
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
