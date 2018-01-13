TCLab: Temperature Control Laboratory
=====================================

The `BYU Arduino Temperature Control Lab <http://apmonitor.com/pdc/index.php/Main/ArduinoTemperatureControl>`__ is designed as a modular, portable, and inexpensive solution for hands-on process control learning.  Heat output is adjusted by modulating current flow to each of two transistors. Thermistors measure the temperatures. Energy from the transistor output is transferred by conduction and convection to the temperature sensor. The dynamics of heat transfer provide rich opportunities to implement single and multivariable control systems. The lab is integrated into a small PCB shield which can be mounted to any `Arduino <https://www.arduino.cc/>`__ or Arduino compatible microcontroller. Experiments can then be programmatically controlled using Python over a USB connection.

The TCLab modules provides access to the temperature control lab using Python, and includes the necessary Arduino firmware for device operation.

Installation
------------

Install using ::

   pip install tclab
   
To upgrade an existing installation, use the command ::

   pip install tclab --upgrade


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
    tclab.TCLab().T1

If everything has worked, you should see the following output message ::

    Connecting to TCLab
    TCLab connected on port XXXX
    20.58

The number returned is the temperature of sensor T1 in °C.

Next Steps
----------

The notebook directory provides examples on how to use the TCLab module.


Course Website
--------------

For more information, instructional videos, and Jupyter notebook examples visit the

* `Arduino temperature control lab page <http://apmonitor.com/pdc/index.php/Main/ArduinoTemperatureControl>`__ on the BYU Process Dynamics and Control course website.
* `CBE 30338 <http://jckantor.github.io/CBE30338/>`__ for the Notre Dame Chemical Process Control course website.
