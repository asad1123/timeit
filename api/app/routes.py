from flask import Blueprint

from . import app, views

# ----------------------------------------------------------------------------

blueprint = Blueprint("timer-api", __name__)

timers_view = views.TimerView.as_view("timers")

blueprint.add_url_rule(
    "/timers/<uuid:id>",
    view_func=timers_view,
    methods=["GET"],
)

blueprint.add_url_rule(
    "/timers",
    defaults={"id": None},
    view_func=timers_view,
    methods=["GET"],
)

blueprint.add_url_rule("/timers", view_func=timers_view, methods=["POST"])

app.register_blueprint(blueprint, url_prefix="/api/v1")
