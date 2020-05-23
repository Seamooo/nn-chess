#!/usr/bin/env python3
from flask import Flask, url_for, send_from_directory, request, jsonify
from chess import Board
import random

app = Flask(__name__, static_url_path='', static_folder='public')

@app.route('/', methods=['GET'])
def get_index():
    return app.send_static_file('index.html')

@app.route('/img/<path:path>')
def send_img(path):
	return send_from_directory('img', path)

@app.route('/ai', methods=['POST'])
def get_move():
	data = request.json
	if 'state' not in data:
		abort(400)
	try:
		board = Board(data['state'])
	except Exception as e:
		abort(400)
	moves = list(board.legal_moves)
	if not moves:
		abort(400)
	move = random.choice(moves)
	print(move)
	return jsonify({'from':str(move)[:2],'to':str(move)[2:]})

#server running on port 4444
if __name__ == '__main__':
    app.run(port=4444)
