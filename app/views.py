from datetime import time
from flask import jsonify
from flask.views import MethodView

# ----------------------------------------------------------------------------

class TimerView(MethodView):

    def get(self, timer_id):
        resp = "default"
        if timer_id is not None:
            resp = timer_id
        
        return jsonify({"data": resp})
    
    def post(self):
        return jsonify({"data": "woot"})