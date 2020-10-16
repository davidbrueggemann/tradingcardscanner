####### IMPORTS ##########
from PIL import Image
from picamera import PiCamera
import RPi.GPIO as GPIO
import time
import sys
import awsupload # own file
import awsdetecttext # own file
import picture # own file

####### CONSTANTS ########
leftCardMovementServoPin=18
rightCardMovementServoPin=2
cardStopperServoPin=24

####### SETUP ##########
def setup():
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(leftCardMovementServoPin,GPIO.OUT)
	GPIO.setup(rightCardMovementServoPin,GPIO.OUT)
	GPIO.setup(cardStopperServoPin,GPIO.OUT)

print "Setup "
setup()

####### START ##########
print "initial Servos on PINs with 50 hz"
leftCardMovementServo=GPIO.PWM(leftCardMovementServoPin,50)
rightCardMovementServo=GPIO.PWM(rightCardMovementServoPin,50)
cardStopperServo=GPIO.PWM(cardStopperServoPin,50)
cardStopperServo.start(2.5)
time.sleep(1)

####### PROCESS LOOP ##########
print "Going into loop"
while True:
	### CARD MOVEMENT leftCardMovementServo ####
	print "Wheel CardMovementServos start"
	leftCardMovementServo.start(15)
	rightCardMovementServo.start(5)
	print "Waiting for 1 sec"
	time.sleep(0.5)
	print "Wheel CardMovementServo stop"
	leftCardMovementServo.stop()
	rightCardMovementServo.stop()
	print "Waiting for 1 sec"
	time.sleep(1)

	# PICTURE
	filename=take_picture()
	crop_picture(filename)
	time.sleep(1)

	### UPLOAD TO AWS ###
	isUploaded=awsupload.upload_file(picFileName)
	print("Upload to AWS successful." if isUploaded else "Upload to AWS failed!")

	### TEXT DETECTION ON AWS ###
	detectedText=awsdetecttext.detect_text(picFileName)
	print ()
	print "Scanned Card: " + detectedText
	print () # get a bit space because this is important

	### CARD STOPPER leftCardMovementServo ####
	print "Little leftCardMovementServo open (90degrees to the side)"
	cardStopperServo.ChangeDutyCycle(7.5)
	print "Waiting for 1 sec"
	time.sleep(1)
	print "Little leftCardMovementServo close (pin upwards)"
	cardStopperServo.ChangeDutyCycle(2.5)
	print "Waiting for 1 sec"
	time.sleep(1)

####### CLEANUP ##########
GPIO.cleanup()
