####### IMPORTS ##########
from PIL import Image
from picamera import PiCamera
import RPi.GPIO as GPIO
import time
import sys
import awsupload # own file

####### CONSTANTS ########
servoPin=18
miniServoPin=24

resolutionW=1024
resolutionH=768

cropX=220 
cropY=210 
cropResultWidth=520 
cropResultHeight=130

####### SETUP ##########
def camera_setup(camera):
	camera.color_effects = (128,128) # grey shades
	camera.rotation = 180
	camera.resolution = (resolutionW, resolutionH)

def setup():
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(servoPin,GPIO.OUT)
	GPIO.setup(miniServoPin,GPIO.OUT)

print "Setup "
setup()
camera = PiCamera()
camera_setup(camera)

####### START ##########
print "initial Servos on PINs with 50 hz"
servo=GPIO.PWM(servoPin,50)
miniServo=GPIO.PWM(miniServoPin,50)
miniServo.start(2.5)
time.sleep(1)

####### PROCESS LOOP ##########
print "Going into loop"
while True:
	### CARD MOVEMENT SERVO ####
	print "Wheel Servo left start"
	servo.start(15)
	print "Waiting for 1 sec"
	time.sleep(1)
	print "Wheel Servo left stop"
	servo.stop()
	print "Waiting for 1 sec"
	time.sleep(1)

	### CAMERA ###
	print "Take a picture"
	timestamp=time.strftime("%Y%m%d%H%M%S")
	picFileName="testfoto"+"_"+timestamp+".jpg"
	camera.capture(picFileName)
	print "Picture Taken!" # See {0}_{1}.jpg!".format(set_name,timestamp)

	### PIC CROP ###
	print "Crop the picture to the needed data"
	pic = Image.open(picFileName)
	pic.crop((cropX, cropY, cropX+cropResultWidth, cropY+cropResultHeight)).save(picFileName)
	time.sleep(1)

	### UPLOAD TO AWS ###
	isUploaded=awsupload.upload_file(picFileName)
	print("Upload to AWS successful." if isUploaded else "Upload to AWS failed!")

	### CARD STOPPER SERVO ####
	print "Little Servo open (90degrees to the side)"
	miniServo.ChangeDutyCycle(7.5)
	print "Waiting for 1 sec"
	time.sleep(1)
	print "Little Servo close (pin upwards)"
	miniServo.ChangeDutyCycle(2.5)
	print "Waiting for 1 sec"
	time.sleep(1)

####### CLEANUP ##########
GPIO.cleanup()
