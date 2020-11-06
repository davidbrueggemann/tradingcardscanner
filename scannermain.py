######## IMPORTS ##########
from PIL import Image
from picamera import PiCamera
import RPi.GPIO as GPIO
import time
import sys
import getopt
import awsupload # own file
import awsdetecttext # own file
import picture # own file
import textfile # own file

####### CONSTANTS ########
leftCardMovementServoPin=18
rightCardMovementServoPin=2
cardStopperServoPin=24
cardUploadEnabled=True #can be deactivated by input param
cameraEnabled=True #can be deactivated by input param
amountOfCards=24 # number of cards in card pile # TODO needs to be dynamic
cardsProcessed=0 # iterator for cardpile
startWheelTime=0.55 # default wheel time

####### STARTSCREEN ########
def startscreen():
	print '========================'
	print '| Trading Card Scanner |'
	print '========================'
	print ''
	print 'Number of arguments:', len(sys.argv), 'arguments.'
	print 'Argument List:', str(sys.argv)

####### PARAMETERHANDLING #########
def parameterhandling():
	try:
		opts, args = getopt.getopt(sys.argv[1:],'hac')
	except getopt.GetoptError:
		print 'INFO: No parameters given'
	for opt, arg in opts:
      		if opt == '-h':
        		print 'scannermain.py -a -c'
			sys.exit()
		elif opt == '-a':
			print "deactivate AWS Upload"  
			cardUploadEnabled=False 
      		elif opt == "-c":
			print "deactivate Camera and AWS upload"
			cardUploadEnabled=False
			cameraEnabled=False
		else:
			cardUploadEnabled=True
			cameraEnabled=True

####### SETUP ##########

def setup():
	print "Setup Servos"
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(leftCardMovementServoPin,GPIO.OUT)
	GPIO.setup(rightCardMovementServoPin,GPIO.OUT)
	print "initial Servos on PINs with 50 hz"
	GPIO.setup(cardStopperServoPin,GPIO.OUT)

######## INIT SCRIPT ##########
startscreen()
parameterhandling()
setup()
cardStopperServo=GPIO.PWM(cardStopperServoPin,50)
leftCardMovementServo=GPIO.PWM(leftCardMovementServoPin,50)
rightCardMovementServo=GPIO.PWM(rightCardMovementServoPin,50)

####### WHEELTIME CALC ########
def adjustWheeltime():
	# control wheel time based on cards in pile
	tempCardsInPile=amountOfCards-cardsProcessed
	if tempCardsInPile>19:
		return startWheelTime
	elif tempCardsInPile>9:
		return startWheelTime*0.90 # Down to 90 percent
	else:
		return startWheelTime*0.70 # Down to 70 percent

####### WHEELCONTROL #########
def wheelsStart():
	print "Wheel CardMovementServos start"
	leftCardMovementServo.start(15)
	rightCardMovementServo.start(5)

def wheelsStop():
	print "Wheel CardMovementServo stop"
	leftCardMovementServo.start(0)
	rightCardMovementServo.start(0)

####### START ##########
cardStopperServo.start(2.5) # put cardholder in position
wheelsStart() # get the first card from pile in postion
time.sleep(0.05)
wheelsStop()
# ready to start with loop
time.sleep(1)

####### PROCESS LOOP ##########
print "Going into loop"
while cardsProcessed<=amountOfCards:
	### CARD MOVEMENT leftCardMovementServo ####
	wheelsStart()
	wheeltime=adjustWheeltime()
	print "spinning Wheel for ", wheeltime," sec"
	time.sleep(wheeltime)
	wheelsStop()
	print "Waiting for 1 sec"
	time.sleep(1)

	# PICTURE
	if cameraEnabled is True:
		picfilename=picture.take()
		picture.crop(picfilename)
		time.sleep(1)
	else:
		print "Skipped Card capturing"

	# AWS
	if cardUploadEnabled is True:
		### UPLOAD TO AWS ###
		print "Uploading to AWS"
		isUploaded=awsupload.upload_file(picfilename)
		print("Upload to AWS successful." if isUploaded else "Upload to AWS failed!")
		
		### TEXT DETECTION ON AWS ###
		print "Detecting text by uploaded picture"
		detectedText=awsdetecttext.detect_text(picfilename)
		print ()
		print "Scanned Card: " + detectedText
		print () # get a bit space because this is important
		if detectedText:
			textfile.cardNameToTextfile(detectedText)
			cardsProcessed+=1 #increment card count
	else:
		print "Skipped AWS Upload"
		cardsProcessed+=1 #increment card count
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
