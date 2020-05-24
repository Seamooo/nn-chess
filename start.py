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

# not really mcts at the moment
# closer to randomised minimax

def dfs(state, num_searches, isplayer):
	comp = max if isplayer else min
	board = Board(state)
	if(board.is_checkmate()):
		return 0.0 if isplayer else 1.0
	if(board.is_stalemate()):
		return 0.5
	if(board.can_claim_draw()):
		return 0.5
	rv = 0.0 if isplayer else 1.0
	moves = list(board.legal_moves)
	# if number of nodes to search exceeds the search limit provided
	# score all nodes
	if(len(moves) > num_searches):
		for move in moves:
			board.push(move)
			rv = comp(rv,score(board.fen()))
			board.pop()
		return rv
	search_move = [False for _ in range(len(moves))]
	search_count = 0
	i = 0
	while i < len(moves):
		inc = min(60, len(moves)-i)
		# gives 50% chance for all nodes to be searched
		# TODO make an adjustable probability parameter
		tp = random.randrange(1<<inc)
		while tp > 0:
			if(tp&1):
				search_move[i] = True
				search_count += 1
			tp >>= 1
		i += inc
	score_count = len(moves) - search_count
	nodes_per_search = 0
	if(search_count != 0):
		nodes_per_search = (num_searches - score_count) // search_count
	vals = []
	for i in range(len(moves)):
		move = moves[i]
		if search_move[i]:
			board.push(move)
			rv = comp(rv,dfs(board.fen(), nodes_per_search, not isplayer))
			board.pop()
		else:
			board.push(move)
			rv = comp(rv, score(move))
			board.pop()
	return rv

def get_move(state):
	#assume both players play the best moves
	#states where you play, take the maximum calculated as rv
	#states where opponent plays, take the min calculated as rv
	#limit number of searches artificially for now
	#choose better numbers later
	print('started search over state', state)
	search_limit = 1000
	board = Board(state)
	mx = 0
	rv = None
	vals = []
	for move in board.legal_moves:
		board.push(move)
		val = dfs(board.fen(), search_limit, False)
		if(val > mx):
			rv = move
			mx = val
		board.pop()
		vals.append((str(move), val))
	print(vals)
	print('found move', rv)
	return rv

@app.route('/ai', methods=['POST'])
def ai_move():
	data = request.json
	if 'state' not in data:
		return 'bad request', 400
	try:
		move = get_move(data['state'])
	except Exception as e:
		print(e)
		return 'bad request', 400
	return jsonify({'from':str(move)[:2],'to':str(move)[2:]})

#server running on port 4444
if __name__ == '__main__':
    app.run(port=4444)
