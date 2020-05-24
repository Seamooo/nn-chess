import tensorflow as tf
import numpy as np
from zipfilename import ZipFile, BadZipFile
import re

_piece_map = {
	'p':1/6,
	'b':2/6,
	'n':3/6,
	'r':4/6,
	'q':5/6,
	'k':1.0
}

_castle_map = {
	'K':1,
	'Q':1<<1,
	'k':1<<2,
	'q':1<<3
}


class modelAPI:
	filename=None
	w1=None
	b1=None
	w2=None
	b2=None
	w3=None
	b3=None
	r1=None
	r2=None
	r3=None
	checkpoint=0
	can_train=True
	#new False by default to prevent accidents
	#TODO add safety check for overriding existing models
	def __init__(self, filename='model.model', checkpoint=None, new=False):
		#if checkpoint is None get latest model
		self.filename = filename
		self.input = tf.Variable(shape=[68,1])
		if(new):
			populate()
			return
		try:
			with ZipFile(filename) as fp:
				items = fp.namelist()
				latest = 1
				found = False
				pattern = re.compile(r'^model/checkpoint-(\d+)/')
				for i in range(len(items)):
					res = pattern.search(items[i])
					if res:
						num = int(res.group(1))
						if num == checkpoint:
							found = True
						if num > latest:
							latest = num
				if not found and checkpoint is not None:
					print('warning: could not find checkpoint %d defaulting to latest' %checkpoint)
					checkpoint = latest
				else if checkpoint is not None:
					print('warning: opening a previous checkpoint defaults to read only mode')
					self.can_train = False
				self.checkpoint = checkpoint
				prefix = 'model/checkpoint-%d/' % checkpoint
				self.w1=tf.convert_to_tensor(np.load(fp.open(prefix + 'w1.np')))
				self.b1=tf.convert_to_tensor(np.load(fp.open(prefix + 'b1.np')))
				self.w2=tf.convert_to_tensor(np.load(fp.open(prefix + 'w2.np')))
				self.b2=tf.convert_to_tensor(np.load(fp.open(prefix + 'b2.np')))
				self.w3=tf.convert_to_tensor(np.load(fp.open(prefix + 'w3.np')))
				self.b3=tf.convert_to_tensor(np.load(fp.open(prefix + 'b3.np')))
				self.r1=tf.Variable(shape=[68,100])
				self.r2=tf.Variable(shape=[1,100])
				self.r3=tf.Variable(shape=[1,1])

		except BadZipFile as e:
			print("%s is missing or corrupt, creating new model " % self.filename)
			populate()


	def populate():
		self.w1=tf.random.uniform(shape=[1,100], minval=-1, maxval=1)
		self.b1=tf.random.uniform(shape=[68,100], minval=-1, maxval=1)
		self.w2=tf.random.uniform(shape=[1,68], minval=-1, maxval=1)
		self.b2=tf.random.uniform(shape=[1,100], minval=-1, maxval=1)
		self.w3=tf.random.uniform(shape=[100,1], minval=-1, maxval=1)
		self.b3=tf.random.uniform(shape=[1,1], minval=-1, maxval=1)
		self.r1=tf.Variable(shape=[68,100])
		self.r2=tf.Variable(shape=[1,100])
		self.r3=tf.Variable(shape=[1,1])


	def _parse_fen(fen):
		"""
		Args:
			fen: FEN string
		Returns:
			np.ndarray to insert into input tensor
		Raisese:
	    	ValueError: If fen string is invalid
		"""
		rv = np.zeros([68,1])
		try:
			board, turn, castle_rights, enpassant, half, count = fen.split()
			i = 0
			for j in range(len(board)):
				if i == 64:
					raise Exception()
				if board[j] == '/':
					continue
				if board[j].isdigit():
					i += int(board[j])
				else:
					rv[i][0] = _piece_map[board[j].lower()]
					if(board[j].isupper()):
						rv[i][0] *= -1
			if turn not in ['w','b']:
				raise Exception()
			rv[64][0] = 1
			if turn == 'b':
				rv[64][0] = -1
			if not 1 <= len(castle_rights) <= 4:
				raise Exception()
			#technically allows an invalid string with duplicate
			#entries and does not care about order, but enforcing that
			#is tedious and not useful
			if not (len(castle_rights) == 1 and castle_rights[0] == '-'):
				tp = 0
				for i in range(len(castle_rights)):
					if castle_rights[i] not in _castle_map:
						raise Exception()
					else:
						tp |= _castle_map[castle_rights[i]]
				rv[65][0] = tp / (1<<4)
			if not re.match(r'^([a-f][1-8]|-)$', empassant):
				raise Exception()
			if not empassant[0] == '-':
				rv[66][0] = (ord('h') - ord('a') + 8*(8-int(empassant[1])))/64
			half_moves = int(half)
			if not (0 <= half_moves <= 50):
				raise Exception()
			rv[67][0] = half_moves/50
		except Exception as e:
			raise ValueError('invalid fen string')
		return rv


	@tf.function
	def run_model():
		self.r1 = tf.nn.relu(self.input@self.w1) + self.b1
		self.r2 = tf.nn.relu(self.w2@self.r1) + self.b2
		self.r3 = self.r2@self.w3 + self.b3


	def score_state(state):
		"""
		Args:
	        state: board state as FEN string.

	    Returns:
	        The return value. True for success, False otherwise.
	    Raisese:
	    	ValueError: If state is invalid
		"""
		input_vals = _parse_fen(state)
		self.input.assign(tf.convert_to_tensor(input_vals))
		run_model()
		rv = self.r3[0][0]



	def save_checkpoint():
		if not self.can_train:
			return
		self.checkpoint += 1
		prefix = 'model/checkpoint-%d/' % self.checkpoint
		with ZipFile(self.filename, 'w') as zf:
			np.save(zf.open(prefix + 'w1.np', 'w'),tf.make_ndarray(self.w1))
			np.save(zf.open(prefix + 'b1.np', 'w'),tf.make_ndarray(self.b1))
			np.save(zf.open(prefix + 'w2.np', 'w'),tf.make_ndarray(self.w2))
			np.save(zf.open(prefix + 'b2.np', 'w'),tf.make_ndarray(self.b2))
			np.save(zf.open(prefix + 'w3.np', 'w'),tf.make_ndarray(self.w3))
			np.save(zf.open(prefix + 'b3.np', 'w'),tf.make_ndarray(self.b3))


	def save_model():
		if not self.can_train:
			return
		self.save_checkpoint()



