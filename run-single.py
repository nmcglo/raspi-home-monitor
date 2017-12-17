import sys
import os
import dropbox
import picamera
import subprocess
from gpiozero import MotionSensor
from time import sleep
import datetime
from twilio.rest import Client


ACCOUNT_SID = os.environ['TWILIOSID']
AUTH_TOKEN = os.environ['TWILIOTOKEN']
KEY = os.environ['DBKEY']
SECRET = os.environ['DBSECRET']
TOKEN = os.environ['DBTOKEN']
toNum = os.environ['TONUM']
fromNum = os.environ['FROMNUM']

client = Client(ACCOUNT_SID, AUTH_TOKEN)




outdir = "/home/neil/raspi-home-monitor/output/"

PHOTOFLAG = False
VIDEOFLAG = True
TESTFLAG = False
vidLength = 10 #seconds
if len(sys.argv) > 1: #then there are command line arguments
    if '-v' in sys.argv:
        PHOTOFLAG = False
        VIDEOFLAG = True
        if len(sys.argv) > 2:
            vidLength = int(sys.argv[2]) #If video, then there is the optional length argument
    if '-t' in sys.argv:
        PHOTOFLAG = False
        TESTFLAG = True

def getValidFilename(baseName, ext):
    currentNum = 0
    with open("num.txt",'r') as nf:
        try:
            currentNum = int(nf.read())
        except:
            currentNum = 0

    nextNum = currentNum+1

    with open("num.txt",'w') as nf:
        nf.write(str(nextNum))

    validName = baseName + '-' + str(nextNum) + ext

    return validName


#CAPTURING

def capture():
    print("Capturing...")

    baseName = "vid"
    ext = ".h264" #TODO figure out the video extension
    filename = getValidFilename(baseName,ext)

    with picamera.PiCamera() as camera:
        camera.resolution = (1296, 972)
        camera.start_recording(outdir + filename)
        camera.wait_recording(vidLength)
        camera.stop_recording()

    return filename



def convert(filename):
    print("Converting...")

    base = filename.split('.')[0]
    convName = base + ".mp4"

    subprocess.call(["MP4Box", "-add", "output/" + filename, "output/" + convName])

    return convName


#DROPBOX UTILITIES

#Uploads a file to the dropbox client
def upload(dbclient, filename):
    with open("output/" + filename, 'rb') as f:
        data = f.read()

    writepath = "/"
    writepath += filename

    response = dbclient.files_upload(data,writepath,mode=dropbox.files.WriteMode.add)

    print("uploaded:", response)


#TWILIO

def send(txtbody):
    client.messages.create(
    to=toNum,
    from_=fromNum,
    body=txtbody
    )

#MAIN

if __name__ == '__main__':
    pir = MotionSensor(4)
    firstRun = True
    while True:
        if not firstRun:
            sleep(10) #sleep for 30 seconds to avoid repeated alarms
        firstRun = False
        if pir.motion_detected:
            theTime = datetime.datetime.now().time()
            message = "Motion detected! " + str(theTime)
            print(message)

            try:
                filename = capture()
            except:
                print("Failed to capture")

            try:
                convName = convert(filename)
            except:
                print("Failed to convert")
                continue
                

            local = False

            try:
                dbclient = dropbox.Dropbox(TOKEN)
            except:
                print("Client didn't connect!!! Recording Locally")
                local = True

            if not local:
                print("Client Connected")
                print("Uploading to Dropbox")
                try:
                    upload(dbclient, convName)
                except:
                    print("Failed upload")

            try:
                send(message)
            except:
                print("Error sending message")

            print("\n-------------\n")