import subprocess
import time
import RPi.GPIO as GPIO

subprocess.run(['python LCD.py face.jpg'], shell=True)


GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
    left = GPIO.input(16)
    if left == False:
        print("Left pressed")
        subprocess.run(['aplay beach3.wav'], shell=True)
        time.sleep(1)
    print("Done")

    right = GPIO.input(20)
    if right == False:
        print("Right pressed")
        subprocess.run(['python LCD.py badair.jpg'], shell=True)
        time.sleep(5)


        subprocess.run(['python LCD.py goodair.jpg'], shell=True)
        time.sleep(5)
    print("Done")

