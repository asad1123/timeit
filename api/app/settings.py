import os

# ----------------------------------------------------------------------------

MONGO_URI = os.environ["MONGO_URI"]
MONGO_TIMER_STORAGE_COLLECTION = os.environ["MONGO_TIMER_STORAGE_COLLECTION"]

MQ_BROKER_HOST = os.environ["MQ_BROKER_HOST"]
MQ_BROKER_PORT = os.environ["MQ_BROKER_PORT"]
MQ_QUEUE_NAME = os.environ["MQ_QUEUE_NAME"]
