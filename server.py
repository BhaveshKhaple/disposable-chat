from flask import Flask, send_from_directory
import threading

app = Flask(__name__, static_folder='.')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(debug=False, port=5000, use_reloader=False)