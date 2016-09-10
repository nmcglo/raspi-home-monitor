from gpiozero import MotionSensor
from time import sleep
import datetime

pir = MotionSensor(4)
while True:
    if pir.motion_detected:
        theTime = datetime.datetime.now().time()
        print("Motion detected! ", theTime)
