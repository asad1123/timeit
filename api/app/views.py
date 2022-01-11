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
from . import mq_client

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


class TimerView(ApiView):

    serializer = TimerSchema()
    deserializer = TimerSchema()
    model = Timer

    def get(self, id: str) -> Union[Dict, List[Dict]]:
        current_time = int(time.time())

        timer = self._get_by_id(id)

        time_to_trigger = timer.expiry_time - current_time
        if time_to_trigger < 0:
            time_to_trigger = 0

        return self.serializer.dump({"id": timer.id, "time_left": time_to_trigger})

    def _get_by_id(self, id):
        try:
            return Timer.objects.get({"_id": id})
        except Timer.DoesNotExist:
            abort(
                Response(
                    status=HTTPStatus.NOT_FOUND,
                    response=json.dumps({"error": f"timer id {id} does not exist"}),
                )
            )

    def post(self) -> Dict:

        body = self.get_request_data()

        now = int(time.time())
        delta = body["hours"] * 60 * 60 + body["minutes"] * 60 + body["seconds"]
        expiry = now + delta
        url = body["url"]

        timer = Timer(id=uuid4(), expiry_time=expiry, url=url).save()

        message = {"id": str(timer.id), "url": timer.url, "expiry_time": expiry}
        mq_client.publish("timers", json.dumps(message))

        return self.serializer.dump({"id": timer.id})
