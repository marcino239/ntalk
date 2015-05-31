import cPickle as pickle
import sys
import re

from run import createModel, getModelParamsFromName
from run import TEXT_NAME, DATA_DIR, MODEL_PARAMS_DIR, WORD_LIST_FILE

def testModel( textName ):

  print( 'Loading word list' )
  word_list = pickle.load( open( word_list_file, 'rb' ) )
  print( 'Got %d words' % len( word_list ) )
	
  print "Creating model from %s..." % textName
  model = createModel( getModelParamsFromName( textName ) )

  model.enableInference()

  for l in sys.stdin:
	l = l.lower()

    # read line to process
	words = re.split( '\W+', l )

	flag, encoded_words = encodeWords( words, word_list )
	if flag:
		continue
		
	predicted_words = []
	sentence = []
	model.resetSequenceStates()
	for e in encoded_words:
	  result = model.run({
        "word_num": e
      })
      sentence.apply( word_list[ int( result.inferences["multiStepBestPredictions"][1] ) ] )

	print( sentence )

if __name__ == "__main__":
	testModel( TEXT_NAME ) 
