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



```
