from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/mark_square')
def mark_square():
    pass


if __name__ == '__main__':
    app.run()
