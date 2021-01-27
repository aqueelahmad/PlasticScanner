#loading data from csv
import pandas as pd
import numpy as np
import tensorflow as tf

#print version to make sure we are at the same page
print(tf.__version__)
from tensorflow.keras import layers
from tensorflow.keras.layers.experimental import preprocessing

#import csv files with the collected data
plastic_train = pd.read_csv(
    "sample_data.csv", header=0)

#separate labels from features
plastic_features = plastic_train.copy()
plastic_labels = plastic_features.pop("PlasticType")

#making it into a single numpy array
plastic_features = np.array(plastic_features) 

#normalize data
normalize = preprocessing.Normalization()
normalize.adapt(plastic_features)

#make model, more layers can be added here, also different optimizers can be used
norm_plastic_model = tf.keras.Sequential([
                                        normalize,
                                        layers.Dense(64),
                                        layers.Dense(1)
])

norm_plastic_model.compile(loss = tf.losses.MeanSquaredError(),
                          optimizer = tf.optimizers.Adam(),
                          metrics=['accuracy'])

#fit model, do the hard work
norm_plastic_model.fit(plastic_features, plastic_labels, epochs=10)
norm_plastic_model.summary()

#save model
norm_plastic_model.save("plastic_estimator")

# Convert the model to TF-LITE
converter = tf.lite.TFLiteConverter.from_keras_model(norm_plastic_model)
tflite_model = converter.convert()

# Save the model.
with open('model.tflite', 'wb') as f:
  f.write(tflite_model)

