from flask import Flask, render_template, request
from iotaclient import IotaClient

app = Flask(__name__)
client = IotaClient()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/move', methods=['POST'])
def move():
    client.save_move(request.form['addr_index'], request.form['player'], request.form['x'], request.form['y'])
    return 'ok'


if __name__ == '__main__':
    app.run()
