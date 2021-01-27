#!/bin/bash
echo "Installing all dependencies"
echo "Installing software for screen"
pip3 install adafruit-circuitpython-ssd1306
echo "Installing python imaging lib"
sudo apt-get install python3-pil
echo "Installing numpy"
pip3 install numpy
echo "Installing TF lite"
pip3 install Software/MachineLearningModel/tflite_runtime-2.3.1-cp37-cp37m-linux_armv6l.whl
echo "Installing pandas"
pip3 install pandas
echo "All done and closing"