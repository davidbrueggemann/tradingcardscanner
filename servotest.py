from PIL import Image
from picamera import PiCamera
import RPi.GPIO as GPIO
import time
import sys

def camera_setup(camera):
	camera.color_effects = (128,128)
	camera.rotation = 0
	camera.resolution = (300,100)

servoPin=18
miniServoPin=24

def setup():
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(servoPin,GPIO.OUT)
	GPIO.setup(miniServoPin,GPIO.OUT)

print "Setup "
setup()
camera = PiCamera()
camera_setup(camera)

print "initial Servos on PINs with 50 hz"
servo=GPIO.PWM(servoPin,50)
miniServo=GPIO.PWM(miniServoPin,50)
miniServo.start(2.5)
time.sleep(1)

print "Going into loop"
while True:
	print "Wheel Servo left start"
	servo.start(15)
	print "Waiting for 1 sec"
	time.sleep(1)
	print "Wheel Servo left stop"
	servo.stop()
	print "Waiting for 1 sec"
	time.sleep(1)

	#timestamp=time.strftime("%Y%m%d%H%M%S")
	#camera.capture("testfoto"+"_"+timestamp+".jpg")
	camera.capture("testfoto"+".jpg")
	print "Picture Taken!" # See {0}_{1}.jpg!".format(set_name,timestamp)

	print "Little Servo open (90degrees to the side)"
	miniServo.ChangeDutyCycle(7.5)
	print "Waiting for 1 sec"
	time.sleep(1)
	print "Little Servo close (pin upwards)"
	miniServo.ChangeDutyCycle(2.5)
	print "Waiting for 1 sec"
	time.sleep(1)

GPIO.cleanup()
