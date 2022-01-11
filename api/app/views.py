from http import HTTPStatus
import time
from typing import Dict, List, Union
from uuid import uuid4

from flask import json, jsonify, request, abort
from flask.views import MethodView
from flask.wrappers import Response
from marshmallow.exceptions import ValidationError
import pymodm

from .models import Timer
from .schemas import TimerSchema
from . import app_config, mq_client

# ----------------------------------------------------------------------------


class ApiView(MethodView):

    serializer = None
    deserializer = None
    model = None

    def get_request_data(self) -> Dict:
        try:
            raw_data = request.get_json()
        except TypeError as e:
            abort(
                Response(
                    status=HTTPStatus.BAD_REQUEST,
                    response=json.dumps({"error": "invalid body"}),
                )
            )

        try:
            data = self.deserializer.load(raw_data)
        except ValidationError as e:
            abort(
                Response(
                    status=HTTPStatus.UNPROCESSABLE_ENTITY,
                    response=json.dumps({"error": e.messages}),
                )
            )

        return data

    def get_or_404(self, id):
        try:
            return self.model.objects.get({"_id": id})
        except self.model.DoesNotExist:
            abort(
                Response(
                    status=HTTPStatus.NOT_FOUND,
                    response=json.dumps({"error": f"id {id} could not be found"}),
                )
            )


class TimerView(ApiView):

    serializer = TimerSchema()
    deserializer = TimerSchema()
    model = Timer

    def get(self, id: str) -> Union[Dict, List[Dict]]:
        current_time = int(time.time())

        timer = self.get_or_404(id)

        # compute time to trigger this timer job
        # return 0 if that time has already elapsed
        time_to_trigger = timer.expiry_time - current_time
        if time_to_trigger < 0:
            time_to_trigger = 0

        return self.serializer.dump({"id": timer.id, "time_left": time_to_trigger})

    def post(self) -> Dict:

        body = self.get_request_data()

        # we will compute the expiry as a UTC epoch
        # this is what we will store in the database
        now = int(time.time())
        delta = body["hours"] * 60 * 60 + body["minutes"] * 60 + body["seconds"]
        expiry = now + delta

        url = body["url"]

        timer = Timer(id=uuid4(), expiry_time=expiry, url=url).save()

        # put this timer on the queue for processing
        message = {"id": str(timer.id), "url": timer.url, "expiry_time": expiry}
        mq_client.publish(app_config["MQ_QUEUE_NAME"], json.dumps(message))

        return self.serializer.dump({"id": timer.id})
