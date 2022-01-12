from flask import Flask
from pymodm import connect

from . import settings
from .mq import mq

# ----------------------------------------------------------------------------

app = Flask(__name__)

app.config.from_object(settings)
app_config = app.config

connect(f"{app.config['MONGO_URI']}/{app.config['MONGO_TIMER_STORAGE_COLLECTION']}")
mq_client = mq.MessageQueueClient(
    app_config["MQ_BROKER_HOST"],
    app_config["MQ_BROKER_PORT"],
)

# ----------------------------------------------------------------------------

from . import routes
