# Diagnose and Troubleshooting

The library supplies a simple way to diagnose errors with the TCLab device in 
a function called `diagnose`, which is called as follows:

```python
from tclab import diagnose

diagnose()
```

This function will attempt to find the Arduino device, make a connection and
attempt to exercise the full command set of the device to make sure everything 
is working correctly.

The above code can also be run from a terminal by using

```shell
python -m tclab 
```


## Problems and solutions

### No Arduino device found

1. First confirm that the device is correctly plugged in.
2. Plug it out and back in
3. Try a different port.
4. If no configuration has worked, you may need to install drivers (see below)


### Access denied

A device has been found but you get an error which mentions "Access denied".

If you are using Windows, this can be resolved by going to Device Manager and 
selecting a different port for the device. If the device shows up incorrecty
in the Device Manager, you may need to install drivers (see below)


### Setting heaters makes temperature jump

You may have plugged both of the USB leads into one computer. The device works
best when the barrel-ended jack is plugged into a separate power supply or 
a different computer.


### Setting heater to 100 doesn't raise temperature

You may only have plugged in your device into your computer using one cable.
Your device needs to be plugged in to your computer *and* requires another
connection to a power supply to power the heaters. 
 

## Software fixes
### Install Drivers
*If you are using Windows 10, the Arduino board should connect without additional drivers required.*

For Arduino clones using the CH340G, CH34G or CH34X chipset you may need additional drivers. Only install these if you see a message saying "No Arduino device found." when connecting.

   * [macOS](https://github.com/adrianmihalko/ch340g-ch34g-ch34x-mac-os-x-driver)
   * [Windows](http://www.wch.cn/downfile/65)


### Update Firmware
It is usually best to use the most recent version of the Arduino firmware, 
available from the [TCLab-Sketch repository](https://github.com/jckantor/TCLab-sketch).


### Update TCLab python library
If you find that the code supplied in the documentation gives errors about 
functions not being found, or if you installed tclab a long time ago, you need 
to update the TCLab library. This can be done with the command

```
pip install --update tclab 
```

