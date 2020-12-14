import math


'''
Keys are of the form AAAAAAAA-ZZZZZZZZ etc.
Could use a wider range of characters but stick with these for the moment
In future could extend this to unicode to cover a much bigger range
''' 
ord_max = ord('Z')
ord_min = ord('A')


def key_next(last_key="A"):
	'''
	Given a key get the next key along at the given significance level
	I.e. increment the Nth character by one
	:param last_key: the previous key that we need to increment from
	'''

	last_ord = ord(last_key[-1])
	if last_ord >= ord_max:
		# Append an extra character as no more "space" at that level
		return last_key + "A"

	# Swap the last character with the next one along at that level
	new_char = chr(last_ord + 1)
	return last_key[:-1] + new_char


def key_between(last_key, next_key):
	'''
	Find the midpoint between the two sort keys
	:param last_key: lower value key
	:param next_key: higher value key
	'''
	carry = 0
	index = 0
	output = ""

	# Go through every digit and average them
	# Carry the remainders to the next digits as we go
	while carry != 0 or index == 0:
		# Pad the extra places with 0
		if index >= len(last_key):
			last_ord = 0
		else:
			last_ord = ord(last_key[index]) - ord_min
		if index >= len(next_key):
			next_ord = 0
		else:
			next_ord = ord(next_key[index]) - ord_min
		tot = last_ord + next_ord + carry * (ord_max + 1 - ord_min)
		output_ord = math.floor(tot / 2)
		carry = tot % 2
		output += chr(output_ord + ord_min)
		index += 1

	return output
