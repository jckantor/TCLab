TCLab: Temperature Control Laboratory
=====================================

``TCLab`` provides a Python interface to the
`Arduino Temperature Control Lab <http://apmonitor.com/pdc/index.php/Main/ArduinoTemperatureControl>`_
over a USB interface. ``TCLab`` is implemented as a Python class within
the ``tclab`` package that also includes:

* ``clock`` A Python generator for soft real-time implementation of
  process control algorithms.
* ``Historian`` A Python class to log results of a process control
  experiment.
* ``Plotter`` Provides an historian with real-time plotting within a
  Jupyter notebook.
* ``TCLabModel`` An embedded model of the temperature control lab
  for off-line and faster-than-realtime simulation of process control
  experiments. No hardware needs to be attached to use ``TCLabModel``.

The necessary Arduino firmware for device operation is available at the
`TCLab-Sketch repository <https://github.com/jckantor/TCLab-sketch>`_.

The `Arduino Temperature Control Lab <http://apmonitor.com/pdc/index.php/Main/ArduinoTemperatureControl>`_
is a modular, portable, and inexpensive solution for hands-on process
control learning.  Heat output is adjusted by modulating current flow to
each of two transistors. Thermistors measure the temperatures. Energy
from the transistor output is transferred by conduction and convection
to the temperature sensor. The dynamics of heat transfer provide rich
opportunities to implement single and multivariable control systems.
The lab is integrated into a small PCB shield which can be mounted to
any `Arduino <https://www.arduino.cc/>`_ or Arduino compatible
microcontroller.

Installation
------------

Install using ::

   pip install tclab
   
To upgrade an existing installation, use the command ::

   pip install tclab --upgrade


To install the development version, use the command ::

   pip install git+https://github.com/jckantor/TCLab@development

Hardware setup
--------------

1. Plug a compatible Arduino device (UNO, Leonardo, NHduino) with the
   lab attached into your computer via the USB connection. Plug the DC
   power adapter into the wall.

2. (optional) Install Arduino Drivers

   *If you are using Windows 10, the Arduino board should connect
   without additional drivers required.*

   Mac OS X users may need to install a serial driver. For arduino
   clones using the CH340G, CH34G or CH34X chipset, a suitable driver
   can be found `here <https://github.com/MPParsley/ch340g-ch34g-ch34x-mac-os-x-driver>`__
   or `here <https://github.com/adrianmihalko/ch340g-ch34g-ch34x-mac-os-x-driver>`__.

3. (optional) Install Arduino Firmware

   ``TCLab`` requires the one-time installation of custom firmware on
   an Arduino device. If it hasn't been pre-installed, the necessary
   firmware and instructions are available from the
   `TCLab-Sketch repository <https://github.com/jckantor/TCLab-sketch>`_.

Checking that everything works
------------------------------

Execute the following code ::

    import tclab
    tclab.TCLab().T1

If everything has worked, you should see the following output message ::

    Connecting to TCLab
    TCLab Firmware Version 1.2.1 on NHduino connected to port XXXX
    21.54

The number returned is the temperature of sensor T1 in °C.

Next Steps
----------

The notebook directory provides examples on how to use the TCLab module.

Course Websites
---------------

More information, instructional videos, and Jupyter notebook
examples are available at the following course websites.

* `Arduino temperature control lab page <http://apmonitor.com/pdc/index.php/Main/ArduinoTemperatureControl>`__ on the BYU Process Dynamics and Control course website.
* `CBE 30338 <http://jckantor.github.io/CBE30338/>`__ for the Notre Dame
  Chemical Process Control course website.
