from . import app, views

# ----------------------------------------------------------------------------

timers_view = views.TimerView.as_view("timers")

app.add_url_rule(
    "/timers/<uuid:id>",
    view_func=timers_view,
    methods=["GET"],
)

app.add_url_rule("/timers", view_func=timers_view, methods=["POST"])
