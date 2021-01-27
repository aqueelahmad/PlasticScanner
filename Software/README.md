# Software
In the end there need to be two scripts
1. A program that can run on the raspberry pi that can do the prediction
2. A program that trains the model based on sample data

the first program needs to do the following thing:

- [x] show simple information on an OLED screen
- [x] start scanning when button is pressed
- [x] pulse LED's with a specific pattern one by one
- [x] measure brightness when LED's flash
- [ ] preprocess data, clean it and normalize
- [x] Save measured values for later model training
- [x] predict plastic based on model, TFlite?
- [x] show result on screen.

the second program need to do the following:
- [x] Get a .csv file from the Pi
- [x] Have this as an input for training_model.py located at MachineLearningModel
- [ ] build the correct model using TensorFlow 2 and Keras 
- [ ] train model and save on Pi



# Sample data
Sample data still needs to be made to enable "test" and build the training algorithm 
</br>
</br>


# Setup of Raspberry Pi

Start by installing the latest version of raspberryOS on a microSD card from [here](https://www.raspberrypi.org/software/)

Once booted go through the setup menu and activate wifi

Go to the setup menu and under "(Pi Logo)->Preference-Raspberry Pi Configuration" 
Under interfaces enable:
- ssh
- vnc 
- spi
- i2c


excecute the following commands:
```bash
cd Downloads
git clone https://github.com/Jerzeek/PlasticScanner
cd PlasticScanner
sudo bash install.sh
```

# Using the software
in the folder codeForMK1 there are the following files:
- database_collection.py -------Run this if you want to measure known plastics to build a calibration database
- estimation_front.py -----------Run this if you want to scan a plastic and have the scanner predict what plastic it is made of.
- Plastic_Sense_Config.py ------Has all the information about the board, like the amounth of LEDs connected or to which pin the button is connected
- Plastic_Sense_Functions.py ---This does all the magic for you in the background, it talk to the breakout board and retrieves information (you dont have to change anything here, ever.).
- Plastic_Sense_Definitions.py --This helps the funtions program to execute the right commands (also dont make changes here, ever.).

in the folder MachineLearningModel there are the following files:
- traning_model.py -------Run this to train your model with the .csv file made by the database_collection.py file
- model.tflite ------------This file is made by running the training_model.py file
- plastic_estimator -------Ths folder is made by running the training_model.py file
- test_TFmodel.py ---------Takes the first sample from the test_data.csv and runs it through the TF model, and shows if it is correct.
- test_TFLitemodel.py -----Inputs random data in the model.tflite and shows an output
- sample_data.csv ---------Is used to train the model
- test_data.csv -----------Is used to test the model
- tflite_runtime-2.3.1-cp37-cp37m-linux_armv6l.whl ----Is used to install TFlite on a raspberry pi zero