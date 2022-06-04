import json

from flask import Flask, request, Response
from fancontrol import override_speed, get_current_speed, main
from threading import Thread

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return "<h1>Distant Reading Archive</h1><p>This site is a prototype API for distant reading of science fiction novels.</p>"


@app.route('/set-fan-speed', methods=['GET'])
def override_fan_speed():
    args = request.args
    new_fan_speed_arg = args.get("speed")
    try:
        new_fan_speed = int(new_fan_speed_arg)
    except Exception:
        return Response(
            response=json.dumps({"success": False, "error": "speed variable must be a number"}),
            status=400
        )
    if new_fan_speed > 100 or new_fan_speed < 0:
        return Response(
            response=json.dumps({"success": False, "error": "speed variable must between 0 and 100"}),
            status=400
        )
    Thread(target=lambda: override_speed(new_fan_speed)).start()

    return Response(status=201)


@app.route('/get-fan-speed', methods=['GET'])
def get_fan_speed():
    current_speed = get_current_speed()
    return Response(response=json.dumps({"success": True, "fan_speed": current_speed}), status=200)


Thread(target=main).start()
app.run(host='0.0.0.0', port=2222)
