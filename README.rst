TCLab: Temperature Control Laboratory
=====================================

The `BYU Arduino Temperature Control Lab <http://apmonitor.com/pdc/index.php/Main/ArduinoTemperatureControl>`__ is designed as a modular, portable, and inexpensive solution for hands-on process control learning.  Heat output is adjusted by modulating the voltage to a transistor. A thermistor measures the temperature. Energy from the transistor output is transferred by conduction and convection to the temperature sensor.  The lab is integrated into a small PCB shield which can be mounted to any `Arduino <https://www.arduino.cc/>`__ or Arduino compatible microcontroller. Experiments can then be programmatically controlled using Python over a USB connection.

Installation
------------

Install using ::

   pip install tclab


Hardware setup
--------------

1. Plug the Arduino with the lab attached into your computer via the USB
   connection. Plug the DC adapter into the wall.

2. (optional) Install Arduino Drivers

   *If you are using Windows 10, the Arduino board should connect
   without additional drivers required.*

   Mac OS X users may need to install a serial driver. For arduino
   clones using the CH340G, CH34G or CH34X chipset, a suitable driver
   can be found `here <https://github.com/MPParsley/ch340g-ch34g-ch34x-mac-os-x-driver>`__ 
   or `here <https://github.com/adrianmihalko/ch340g-ch34g-ch34x-mac-os-x-driver>`__.

3. (optional) Install Arduino Firmware

   If you are using your own Arduino board, you will need to flash the
   board with the custom firmware used by the lab. This is done using
   the `Arduino IDE <https://www.arduino.cc/en/Main/Software>`__. The
   script that must be uploaded to the board is found in the sketch directory.

Checking that everything works
------------------------------

Execute the following code ::

    import tclab
    tclab.flash_led()

If everything has worked, you should see the following output message ::

    Opening connection
    TCLab connected via Arduino on port XXXX
    LED On
    LED Off
    Arduino disconnected successfully

The LED on your board should light up for 1 second and then go out.

Course Website
--------------

For more information and instructional videos, visit the `Arduino temperature control lab page <http://apmonitor.com/pdc/index.php/Main/ArduinoTemperatureControl>`__ on the BYU Process Dynamics and Control course website.

## Overview

This TCLab library comprises three main elements:

* An Arduino sketch (TCLab/sketch/sketch.ino) implementing a simple protocol for communicating with the 
Temperature Control Laboratory device.
* A Python library (TCLab/TCLab.py) providing a high level interface with the device.
* A collection of Jupyter notebooks (notebooks/) illustrating concepts in process control. 







