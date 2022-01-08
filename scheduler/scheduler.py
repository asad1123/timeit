from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from marshmallow.exceptions import ValidationError
import pika
import requests
from requests.models import HTTPError
import sys

from schemas import Timer

# ----------------------------------------------------------------------------

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# ----------------------------------------------------------------------------


class TimerExecuter:
    def __init__(self):
        self.scheduler = self._start_scheduler()
        self._start_consumer("192.168.0.158", "timers", self._add_job)

    def _start_scheduler(self):
        scheduler = BackgroundScheduler(timezone="UTC")
        scheduler.add_jobstore(
            jobstore="mongodb",
            alias="mongodb",
            collection="timer-jobs",
            host="192.168.0.158",
            port=27017,
        )
        scheduler.start()

        return scheduler

    def _start_consumer(self, broker_host, message_queue, callback):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=broker_host)
        )
        channel = connection.channel()
        channel.queue_declare(queue=message_queue)
        channel.basic_consume(queue=message_queue, on_message_callback=callback)

        logger.info("Starting consumer --------")
        channel.start_consuming()

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
            jobstore="mongodb",
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
