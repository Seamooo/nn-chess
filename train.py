#!/usr/bin/env python3
print('placeholder file')

"""
model planning:
input neurons:
	what piece is on each square
	colour turn
	castle information
	En passant target square
	halfmove count
	serialize as pawn, bishop, knight, rook, queen, king
	having positive values for white and negative values for black
	serialize between -1 and 1
	pawn = 1/6, bishop = 2/6, knight = 3/6, rook = 4/6, queen = 5/6, king = 6/6
	[0->63]=board
	64=colour turn (-1,1)
	65=serialized can castle ({0..1<<4}/1<<4)
	66=en passant square (1/64->64/64 or -1 if not set)
	67=halfmove count (0/50->50/50)
output:
	0 < n < 1 scoring state for white
	hence 1 - n is score for black

architecture:
	[68,1] input
	[1,100] w1
	[68,100] b1
	[1,68] w2
	[1,100] b2
	[100,1] w3
	[1,1] b3
	r1 = relu(input * w1 + b1)
	r2 = relu(w2 * r1 + b2)
	r3 = r2 * w3 + b3
	result = (r3[0][0] + 1)/2
"""

