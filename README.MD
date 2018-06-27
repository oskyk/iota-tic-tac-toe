# Iota tic tac toe

----
## What is Iota tic tac toe?
see [Iota-tic-tac-toe](http://iota-tictactoe.ddns.net)

This project was made as an experiment of capabilities of iota netowk

----
## Prerequisites
* memcached
* pip install -r requirements.txt

----
## Running your iota tic tac toe
1. Run your memcached
2. Run pip install `pip install -r requirements.txt`
3. Copy config/config.example.txt to config/config.txt `cp config/config.example.txt config/config.txt`
4. Edit config/config.txt to suit your needs
5. Run `FLASK_APP=iota-tic-tac-toe.py flask run --host=127.0.0.1 --port=80 &`
6. Run `python ttt-bot.py &`
7. visit [http://127.0.0.1/](http://127.0.0.1/)