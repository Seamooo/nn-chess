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

def score(state):
	return random.random()

#hyper parameter
probability_reduc = 0.8

def dfs(state, num_searches, isplayer, prob):
	comp = max if isplayer else min
	board = Board(state)
	if(board.is_checkmate()):
		return (0 if isplayer else 1, num_searches)
	if(board.is_stalemate()):
		return 0.5, num_searches
	if(board.can_claim_draw()):
		return 0.5, num_searches
	rv = 0 if isplayer else 1
	for move in board.legal_moves:
		if(random.random()<prob):
			if(num_searches > 0):
				num_searches -= 1
				board.push(move)
				ret, num_searches = dfs(board.fen(), num_searches, isplayer, prob*probability_reduc)
				rv = comp(rv,ret)
				board.pop()
				continue
		board.push(move)
		comp(rv,score(board.fen()))
		board.pop()
	return rv, num_searches


def get_move(state):
	#assume both players play the best moves
	#states where you play, take the maximum calculated as rv
	#states where opponent plays, take the min calculated as rv
	#limit number of searches artificially for now
	#choose better numbers later
	print('started search over state', state)
	search_limit = 100
	board = Board(state)
	mx = 0
	rv = None
	for move in board.legal_moves:
		board.push(move)
		val, _ = dfs(board.fen(), search_limit, False, probability_reduc)
		if(val > mx):
			rv = move
			mx = val
		board.pop()
	print('found move', rv)
	return rv

@app.route('/ai', methods=['POST'])
def ai_move():
	data = request.json
	if 'state' not in data:
		return 'bad request', 400
		"""
	try:
		move = get_move(data['state'])
	except Exception as e:
		print(e)
		return str(e), 400
		"""
	move = get_move(data['state'])
	return jsonify({'from':str(move)[:2],'to':str(move)[2:]})

#server running on port 4444
if __name__ == '__main__':
    app.run(port=4444)
