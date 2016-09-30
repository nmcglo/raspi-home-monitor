# raspi-home-monitor
A python app for simple home monitoring. Can take photos or videos and upload to dropbox.


This is a python hobby project. It will be a series of scripts that run on Raspberry Pi devices with various purposes that
are meant to control and monitor a home. For instance, current proof of concept features a motion sensing raspberry pi that
texts me (Using Twilio) when motion is detected in my apartment. It also then triggers another Raspberry Pi device on my network to record
video of the area and uploads to Dropbox.

Currently I am working on creating an integration with Amazon's Echo and associated Alexa service to allow for voice control
of this system. This requires use of Amazon's AWS-Lambda service and Alexa skills API.
