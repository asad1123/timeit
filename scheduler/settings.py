import os

# ----------------------------------------------------------------------------

MONGO_URI = os.environ["MONGO_URI"]
MONGO_JOB_SCHEDULER_COLLECTION = os.environ["MONGO_JOB_SCHEDULER_COLLECTION"]

MQ_BROKER_HOST = os.environ["MQ_BROKER_HOST"]
MQ_BROKER_PORT = os.environ["MQ_BROKER_PORT"]
MQ_EXCHANGE = os.environ["MQ_EXCHANGE"]
MQ_QUEUE_NAME = os.environ["MQ_QUEUE_NAME"]
