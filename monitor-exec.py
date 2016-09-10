import sys
import os
import dropbox
import picamera
from time import sleep

outdir = "output/"

PHOTOFLAG = True
VIDEOFLAG = False
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

#Authorization flow
def authorize():
    flow = dropbox.client.DropboxOAuth2FlowNoRedirect(KEY, SECRET)
    # Have the user sign in and authorize this token
    authorize_url = flow.start()
    print ('1. Go to: ' + authorize_url)
    print ('2. Click "Allow" (you might have to log in first)')
    print ('3. Copy the authorization code.')
    code = input("Enter the authorization code here: ").strip()
    access_token, user_id = flow.finish(code)

    return access_token,user_id



#CAPTURING

def photoCapture(filename):
    camera = picamera.PiCamera()
    camera.resolution = (2592, 1944)
    camera.start_preview()
    # Camera warm-up time
    sleep(3)
    camera.capture(outdir + filename)
    f = open(outdir + filename, 'rb')

    return f

def vidCapture(filename):
    camera = picamera.PiCamera()
    camera.resolution = (1296, 972)
    camera.start_recording(outdir + filename)
    camera.wait_recording(vidLength)
    camera.stop_recording()
    f = open(outdir + filename, 'rb')

    return f


#Takes a screencapture - OSX ONLY
def screenCapture(filename):
    os.system("screencapture " + outdir + filename)
    f = open(outdir + filename,'rb')
    return f


#DROPBOX UTILITIES

#Uploads a file to the dropbox client
def upload(client, thefile, filename):
    response = client.put_file(filename, thefile)
    print("uploaded:", response)

#This is to ensure that you don't overwrite a file that has been previously uploaded
def getValidFilename(baseName, ext):
    isInvalidName = True
    validName = None

    while(isInvalidName):
        folder_metadata = client.metadata('',list=True)
        files = [content['path'].split('/')[-1] for content in folder_metadata['contents']]

        files.sort()

        usedNumbers = [fn.split('.')[0].split('-')[-1] for fn in files if baseName in fn]
        usedNumbers.sort()

        if len(usedNumbers) > 0:
            lastNumber = usedNumbers[-1]
        else:
            lastNumber = 0
        newNumber = int(lastNumber) + 1

        validName = baseName + '-' + str(newNumber) + ext

        if validName not in files:
            isInvalidName = False

    return validName


#MAIN

if __name__ == '__main__':
    KEY = os.environ['DBKEY']
    SECRET = os.environ['DBSECRET']

    try:
        TOKEN = os.environ['DBTOKEN']
    except:
        print("There was no Dropbox Token Environment Variable. Proceeding to authorization step")
        TOKEN, userID = authorize()

    client = dropbox.client.DropboxClient(TOKEN)

    print("Client Connected")

    print("Capturing...")

    if PHOTOFLAG is True:
        baseName = "img"
        ext = ".jpg"
        filename = getValidFilename(baseName,ext)
        f = photoCapture(filename)

    elif VIDEOFLAG is True:
        baseName = "vid"
        ext = ".h264" #TODO figure out the video extension
        filename = getValidFilename(baseName,ext)
        f = vidCapture(filename)

    elif TESTFLAG is True:
        baseName = "test"
        ext = ".png"
        filename = getValidFilename(baseName,ext)
        f = screenCapture(filename)

    else:
        print("Error during capture - no flags set somehow. Exiting...")
        exit(1)

    print("Captured.")

    print("Uploading to Dropbox")
    upload(client, f, filename)
