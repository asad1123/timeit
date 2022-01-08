import os

# ----------------------------------------------------------------------------

MONGO_URI = f'mongodb://{os.environ["DATABASE_HOST"]}:{os.environ["DATABASE_PORT"]}/{os.environ["DATABASE_NAME"]}'
