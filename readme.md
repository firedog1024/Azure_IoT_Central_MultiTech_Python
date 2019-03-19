# Azure IoT Central sample Python code for MultiTech Conduit Gateway

## What is this?

Sample code to show how to get the MultiTech Conduit Gateway Hardware (http://www.multitech.net/developer/products/multiconnect-conduit-platform/) to talk to Azure IoT Central (https://apps.azureiotcentral.com/).

## Features

* Works with MultiTech Conduit gateway hardware
* Uses simple MQTT library to communicate to Azure IoT Central
* Simple code base designed to illustrate how the code works and encourage hacking (~300 lines of core code w/ comments)
* Supports the use of Azure IoT Device Provisioning Service (DPS) for registering the device in IoT Central
* IoT Central features supported
    * Telemetry data - Temperature every 5 seconds
    * Properties - Device sends a die roll number every 15 seconds
    * Settings - Acknowledges receipt of setting property changes
    * Commands - Shows receipt of commands and the parameters passed

## Dependencies:

You need to install mlinux 4.0 onto the MultiTech Conduit box so that you have a version of Python 2.7 that supports SSL (http://www.multitech.net/developer/software/mlinux/upgrading-mlinux/).

Install the following dependencies on your development machine using Python 2.7 pip.

Httplib2:
```sh
pip install httplib2
```

Paho:
```sh
pip install paho-mqtt
```

## Config the code

We need to copy some values from the IoT Central device into the config.py file so it can connect to IoT Central.

Click the device you created in IoT Central. We are going to copy "Scope ID", "Device ID", and "Primary Key" values into the respective positions in the config.py file.

```python
# Scope identifier for the application - found in IoT Central in the Administration -> Device Connection page
SCOPE_ID = '<insert scope identifier here>'

# Application key - found in IoT Central in the Administration -> Device Connection page
APP_KEY = '<insert application key here>'

# device identity, this can be pre registered in the IoT Central application or will be registered via DPS and 
# placed in the Unassociated Devices page waiting to be associated with a template
DEVICE_NAME = '<insert device identifier here>'
```

Optionally you can add the "Model ID" if you want to use the auto-associate feature of IoT Central.

```python
# template model identifier - found in IoT Central in the Device Explorer at the top of the page
MODEL_ID = ''
```

## Prep the SD Card

Copy all the files to files in the repo to a directory on the sd card.  Then also copy the following directories from your Python pip install package directory to the same directory on the sd card.  If you do not know where the packages are on your development box then use the following command.

```sh
pip show httplib2
```

Copy the following directories:

* httplib2
* paho 

## Run the demo

Eject the sd card from your computer and put it into the MultiTech Conduit. 

From the SSH or serial terminal cd to the sd card and directory you created and issue the command:

```sh
python main.py
```

## What Now?

You have the basics now go play and hack this code to send other data to Azure IoT Central.  If you want to create a new device template for this you can learn how to do that with this documentation https://docs.microsoft.com/en-us/azure/iot-central/howto-set-up-template.

How about creating a rule to alert when the temperature exceed a certain value.  Learn about creating rules here https://docs.microsoft.com/en-us/azure/iot-central/tutorial-configure-rules.

For general documentation about Azure IoT Central you can go here https://docs.microsoft.com/en-us/azure/iot-central/.

Have fun!

