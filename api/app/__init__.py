from flask import Flask
from pymodm import connect

from . import settings
from .mq import mq

# ----------------------------------------------------------------------------

app = Flask(__name__)
app.config.from_object(settings)

connect(app.config["MONGO_URI"])
mq_client = mq.MessageQueueClient("mq", "timers")

# ----------------------------------------------------------------------------

from . import routes
