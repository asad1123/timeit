from http import HTTPStatus
import time
from typing import Dict, List, Union
from uuid import uuid4

from flask import json, jsonify, request, abort
from flask.views import MethodView
from flask.wrappers import Response
from marshmallow.exceptions import ValidationError

from .models import Timer
from .schemas import TimerSchema

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


# ----------------------------------------------------------------------------


class TimerView(ApiView):

    serializer = TimerSchema()
    deserializer = TimerSchema()
    model = Timer

    def get(self, id: str) -> Union[Dict, List[Dict]]:

        if id is not None:
            resp = id

        return self.schema.dump({"id": uuid4(), "time_left": 45, "abca": "fajsdf"})

    def post(self) -> Dict:

        body = self.get_request_data()

        now = int(time.time())
        delta = body["hours"] * 60 * 60 + body["minutes"] * 60 + body["seconds"]
        expiry = now + delta

        timer: Timer = Timer(id=uuid4(), expiry_time=expiry).save()

        return self.serializer.dump({"id": timer.id})
