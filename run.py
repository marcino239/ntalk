#!/usr/bin/env python
# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2013, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------
"""
Groups together code used for creating a NuPIC model and dealing with IO.
(This is a component of the One Hot Gym Prediction Tutorial.)
"""
import importlib
import sys
import csv
import datetime
import cPickle as pickle

from nupic.data.inference_shifter import InferenceShifter
from nupic.frameworks.opf.metrics import MetricSpec
from nupic.frameworks.opf.modelfactory import ModelFactory
from nupic.frameworks.opf.predictionmetricsmanager import MetricsManager

import nupic_output


DESCRIPTION = (
  "Starts a NuPIC model from the model params returned by the swarm\n"
  "and pushes each line of input from the gym into the model. Results\n"
  "are written to an output file (default) or plotted dynamically if\n"
  "the --plot option is specified.\n"
  "NOTE: You must run ./swarm.py before this, because model parameters\n"
  "are required to run NuPIC.\n"
)
TEXT_NAME = 'sequence'
WORD_LIST_FILE = 'word_encodings.pkl'
DATA_DIR = '.'
MODEL_PARAMS_DIR = './model_params'
# '7/2/10 0:00'
DATE_FORMAT = '%m/%d/%y %H:%M'

MODEL_DIR = 'model'

_METRIC_SPECS = (
    MetricSpec(field='word_num', metric='multiStep',
               inferenceElement='multiStepBestPredictions',
               params={'errorMetric': 'aae', 'window': 1000, 'steps': 1}),
    MetricSpec(field='word_num', metric='trivial',
               inferenceElement='prediction',
               params={'errorMetric': 'aae', 'window': 1000, 'steps': 1}),
    MetricSpec(field='word_num', metric='multiStep',
               inferenceElement='multiStepBestPredictions',
               params={'errorMetric': 'altMAPE', 'window': 1000, 'steps': 1}),
    MetricSpec(field='word_num', metric='trivial',
               inferenceElement='prediction',
               params={'errorMetric': 'altMAPE', 'window': 1000, 'steps': 1}),
)

def createModel(modelParams):
  model = ModelFactory.create(modelParams)
  model.enableInference({"predictedField": "word_num"})
  return model



def getModelParamsFromName(textName):
  importName = "model_params.%s_model_params" % (
    textName.replace(" ", "_").replace("-", "_")
  )
  print "Importing model params from %s" % importName
  try:
    importedModelParams = importlib.import_module(importName).MODEL_PARAMS
  except ImportError:
    raise Exception("No model params exist for '%s'. Run swarm first!"
                    % textName)
  return importedModelParams



def runIoThroughNupic( inputData, model, textName, word_list ):
  inputFile = open(inputData, "rb")
  csvReader = csv.reader(inputFile)
  # skip header rows
  csvReader.next()
  csvReader.next()
  csvReader.next()

  shifter = InferenceShifter()
  output = nupic_output.NuPICFileOutput([textName])

  metricsManager = MetricsManager(_METRIC_SPECS, model.getFieldInfo(),
                                  model.getInferenceType())

  model.enableLearning()
  counter = 0
  for row in csvReader:
    counter += 1
    reset_flag = bool( row[0] )
    word_num = int( row[1] )

    if reset_flag:
      print( 'resetting model' )
      model.resetSequenceStates()

    result = model.run({
      "word_num": word_num
    })

    result.metrics = metricsManager.update(result)

    if counter % 100 == 0:
      print "Read %i lines..." % counter
      print ("After %i records, 1-step altMAPE=%f", counter,
              result.metrics["multiStepBestPredictions:multiStep:"
                             "errorMetric='altMAPE':steps=1:window=1000:"
                             "field=word_num"])
 
  model.finishLearning()
  model.save( MODEL_DIR )


  inputFile.close()
  output.close()



def runModel( textName, word_list_file ):

  print( 'Loading word list' )
  word_list = pickle.load( open( word_list_file, 'rb' ) )
  print( 'Got %d words' % len( word_list ) )

  print "Creating model from %s..." % textName
  model = createModel(getModelParamsFromName( textName ))
  inputData = "%s/%s.csv" % (DATA_DIR, textName.replace(" ", "_"))
  runIoThroughNupic(inputData, model, textName, word_list )



if __name__ == "__main__":
  print DESCRIPTION
  plot = False
  args = sys.argv[1:]
  runModel( TEXT_NAME, WORD_LIST_FILE )
