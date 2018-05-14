from flask import Flask, render_template, request, redirect
from iotaclient import IotaClient
import json

app = Flask(__name__)
client = IotaClient()


@app.route('/game')
def play():
    return render_template('game.html', Iplayer=request.args['player'], game=request.args['game'])


@app.route('/move', methods=['POST'])
def move():
    client.save_move(request.form['addr_index'], request.form['player'], request.form['x'], request.form['y'])
    return 'ok'


@app.route('/move', methods=['GET'])
def get_move():
    moves = client.get_moves(request.args['addr_index'])
    try:
        my_move = moves[int(request.args['id'])]
        return app.response_class(
            response=json.dumps(my_move),
            mimetype='application/json'
        )
    except IndexError:
        return app.response_class(status=404)


@app.route('/')
def get_game():
    game, player = client.get_match()
    return redirect('/game?player={}&game={}'.format(player, game))


if __name__ == '__main__':
    app.run()
