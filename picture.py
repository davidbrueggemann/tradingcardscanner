####### IMPORTS ##########
from PIL import Image
from picamera import PiCamera
import time
import sys

####### CONSTANTS ########
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

camera = PiCamera()
camera_setup(camera)

def take():
	### CAMERA ###
	print "Take a picture"
	timestamp=time.strftime("%Y%m%d%H%M%S")
	picFileName="testfoto"+"_"+timestamp+".jpg"
	camera.capture(picFileName)
	print "Picture Taken!" # See {0}_{1}.jpg!".format(set_name,timestamp)
	return picFileName

def crop(pictureFileName):
	### PIC CROP ###
	print "Crop the picture to the needed data"
	pic = Image.open(pictureFileName)
	pic.crop((cropX, cropY, cropX+cropResultWidth, cropY+cropResultHeight)).save(pictureFileName)
