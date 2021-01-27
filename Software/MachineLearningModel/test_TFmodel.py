#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""  Takes the first sample from the test_data.csv and runs it through the TF model, and shows if it is correct.   """

#loading data from csv
import pandas as pd
import numpy as np
import tensorflow as tf
#print version to make sure we are at the same page
print(tf.__version__)

#list of plastics
plastics = ["PET", "HDPE", "PCV", "LDPE", "PP", "PS","OTHER"]

#reload model
reloaded_model = tf.keras.models.load_model('plastic_estimator')

#prediction
test_input = pd.read_csv("test_data.csv", header=0)
test_input_type = test_input.pop("PlasticType")
test_input = np.array(test_input.loc[[3]])
prediction = reloaded_model.predict(test_input)

#output
print("the actual number was: ", test_input_type.loc[3] )                               #plastic resin code from file
print("the actual number was: ", plastics[(test_input_type.loc[0]-1)] )                #plastic text based from files
print("trained model thinks it is: ", prediction)                                       #plastic resin code prediction
print("trained model thinks it is: ", plastics[(int(np.around(prediction))-1)])        #plastic text based prediction
