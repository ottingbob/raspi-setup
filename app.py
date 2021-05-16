import subprocess
from flask import Flask

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


# For AARCH64 we can use `sensors` to get temperature info
@app.route("/temp")
def temp_cmd():
    # f = open('/tmp/cpu-temp-output', 'w+')
    # temp_cmd = "which sensors"
    # temp_cmd = "which grep"
    temp_cmd = "id"
    sensors_output = subprocess.run(temp_cmd.split(' '),
                                    capture_output=True,
                                    text=True)
    if sensors_output.returncode != 0:
        app.logger.info(sensors_output.returncode)
        app.logger.info(sensors_output.stdout)
        app.logger.info(sensors_output.stderr)
        return "Failure getting temperature..."
    if sensors_output.stdout is not None:
        for line in sensors_output.stdout.split('\n'):
            app.logger.info(line)
    return "Successfully got temperature"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
