#!/usr/bin/python

import re
import cPickle as pkl

from datetime import datetime, timedelta

in_file_name = '844.txt.utf-8'
word_encodings_file = 'word_encodings.pkl'
sequence_file = 'sequence.csv'

delimiter_string = '\W+'

#import pdb

def encode_words( in_file, word_encodings_file ):
	
	fin = open( in_file, 'rt' )
	word_list = []
	
#	pdb.set_trace()
	
	for l in fin:
		l = l.lower()
		
		words = re.split( delimiter_string, l )
		
		for w in words:
			if len( w ) > 0:
				if not w in word_list:
					word_list.append( w )

	fout = open( word_encodings_file, 'wb')
	pkl.dump( word_list, fout )
	fout.close()
	
	return word_list


def write_sequence( in_file_name, fout, word_encodings ):
	
	fin = open( in_file_name, 'rt' )
	
	reset_flag = True
	i = 0
	start_date = datetime( 2000, 1, 1 )
	
	for l in fin:
		l = l.lower()
		
		words = re.split( delimiter_string, l )
	
		for w in words:
			if len( w ) > 0:
				end_date = start_date + timedelta( days = i )
				fout.write( '%d,%d\n' % (int( reset_flag ), word_encodings.index( w ) ) )
				i = i + 1
				reset_flag = False
			else:
				reset_flag = True


def main():
	#create word encoding list
	word_encodings = encode_words( in_file_name, word_encodings_file )

	fout = open( sequence_file, 'wt' )
	
	fout.write( 'reset, word_num\n' )
	fout.write( 'bool, int\n' )
	fout.write( 'R,\n' )
	
	#create sequences
	write_sequence( in_file_name, fout, word_encodings )

	fout.close()

if __name__ == "__main__":
	main()
