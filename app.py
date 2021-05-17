import json
import subprocess
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def index():
    return "Hello friend"


@app.route("/local")
def local_cmd():
    # Piping commands example
    f = open('/tmp/test', 'w+')
    cmd = "echo hello there dude"
    cmd2 = "grep the /tmp/test"
    subprocess.run(cmd.split(' '), stdout=f, text=True)
    output2 = subprocess.run(cmd2.split(' '), text=True)
    if output2.returncode != 0:
        app.logger.info("ouches")
    else:
        app.logger.info(output2.stdout)
    return "done"


@app.route("/temp")
def temp_cmd():
    json_data_str = "{}"
    with open('/app/mon/cpu_info.json', 'r') as json_file:
        json_data_str = json_file.read()
    json_data = json.loads(json_data_str)
    app.logger.info(json_data)
    return jsonify(json_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
