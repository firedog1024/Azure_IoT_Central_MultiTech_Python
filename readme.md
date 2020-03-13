# Azure IoT Central sample Python code for MultiTech Conduit Gateway or any other python system unable to use the official Azure IoT Python SDK

## What is this?

Sample code to show how to get the MultiTech Conduit Gateway Hardware (http://www.multitech.net/developer/products/multiconnect-conduit-platform/) to talk to Azure IoT Central (https://apps.azureiotcentral.com/).  Will also work for
any other python system unable to use the official Azure IoT Python SDK.

## Features

* Works with MultiTech Conduit gateway hardware and others
* Uses simple MQTT library to communicate to Azure IoT Central
* Simple code base designed to illustrate how the code works and encourage hacking (~300 lines of core code w/ comments)
* Supports the use of Azure IoT Device Provisioning Service (DPS) for registering the device in IoT Central
* IoT Central features supported
    * Telemetry data - Temperature every 5 seconds
    * Properties - Device sends a die roll number every 15 seconds
    * Settings - Acknowledges receipt of setting property changes
    * Commands - Shows receipt of commands and the parameters passed

## Dependencies:

For Multitech:

You need to install mlinux 4.0 onto the MultiTech Conduit box so that you have a version of Python 2.7 that supports SSL (http://www.multitech.net/developer/software/mlinux/upgrading-mlinux/).

Start here for other systems:

Install the following dependencies on your development machine using Python 2.7 pip.  Also works fine with Python 3+

Httplib2:
```sh
pip install httplib2
```

Paho:
```sh
pip install paho-mqtt
```

## Setting up IoT Central application

To connect the device to Azure IoT Central you will need to provision an IoT Central application. This is free for seven days but if you already have signed up for an Azure subscription and want to use pay as you go IoT Central is free as long as you have no more than five devices and do not exceed 1MB per month of data.

Go to https://apps.azureiotcentral.com/ to create an application (you will need to sign in with a Microsoft account identity you may already have one if you use Xbox, office365, Windows 10, or other Microsoft services).

Choose Trial or Pay-As-You-Go.
Select the Sample DevKits template (middle box)
Provide an application name and URL domain name
If you select Pay-As-You-Go you will need to select your Azure subscription and select a region to install the application into. This information is not needed for Trial.
Click "Create"
You should now have an IoT Central application provisioned so lets add a real device. Click Device Explorer on the left. You will now see three templates in the left hand panel (MXChip, Raspberry Pi, Windows 10 IoT Core). We are going to use the MXChip template for this exercise to prevent having to create a new template. Click "MXChip" and click the "+V" icon on the toolbar, this will present a drop down where we click "Real" to add a new physical device. Give a name to your device and click "Create".

You now have a device in IoT Central that can be connected to from the MultiTech Conduit device. Proceed to wiring and configuration.

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

You should see the results of sending data to IoT Central in the terminal and shortly data should start to appear in your IoT Central application.  Note, only temerature data is being sent so be sure to click the temperature eyeball in the IoT Central device explorer measurements screen.

## What Now?

You have the basics now go play and hack this code to send other data to Azure IoT Central.  If you want to create a new device template for this you can learn how to do that with this documentation https://docs.microsoft.com/en-us/azure/iot-central/howto-set-up-template.

How about creating a rule to alert when the temperature exceed a certain value.  Learn about creating rules here https://docs.microsoft.com/en-us/azure/iot-central/tutorial-configure-rules.

For general documentation about Azure IoT Central you can go here https://docs.microsoft.com/en-us/azure/iot-central/.

Have fun!

