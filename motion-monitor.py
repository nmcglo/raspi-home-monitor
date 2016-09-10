import os
from gpiozero import MotionSensor
from time import sleep
import datetime
from twilio.rest import TwilioRestClient
import subprocess

ACCOUNT_SID = os.environ['TWILIOSID']
AUTH_TOKEN = os.environ['TWILIOTOKEN']

client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

toNum = os.environ['CELLNUMBER'] #nope!
fromNum = os.environ['TWILIONUMBER']


def send(txtbody):
    client.messages.create(
    to=toNum,
    from_=fromNum,
    body=txtbody
    )

if __name__ == '__main__':

    pir = MotionSensor(4)
    while True:
        if pir.motion_detected:
            theTime = datetime.datetime.now().time()
            message = "Motion detected! " + str(theTime)
            print(message)
            send(message)
            subprocess.call(["ssh","neil@remotehost", "python3 /home/neil/raspi-home-monitor/monitor-exec.py -v"])
            sleep(10) #sleep for 30 seconds to avoid repeated alarms
