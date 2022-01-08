from flask import Flask
from pymodm import connect

from . import settings

# ----------------------------------------------------------------------------

app = Flask(__name__)
app.config.from_object(settings)

mongo = connect(app.config["MONGO_URI"])

# ----------------------------------------------------------------------------

from . import routes
