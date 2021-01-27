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
- [ ] predict plastic based on model, TFlite?
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

Also at Performance change the video memory to 256mb

excecute the following commands:
```bash
pip3 install scikit-learn
pip3 install matplotlib
pip3 install pandas
pip3 install numpy
sudo apt-get install libatlas-base-dev
cd Downloads
git clone https://github.com/Jerzeek/PlasticScanner
pip3 install adafruit-circuitpython-ssd1306
sudo apt-get install python3-pil


```
