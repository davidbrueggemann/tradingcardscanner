####### IMPORTS ##########
from PIL import Image
from picamera import PiCamera
import picamera.array
import time
import sys

####### CONSTANTS ########
resolutionW = 1024
resolutionH = 768

cropX = 220
cropY = 210
cropResultWidth = 520
cropResultHeight = 130

# User Image Settings
imageVFlip = True       # Flip image Vertically
imageHFlip = True       # Flip image Horizontally

# User Motion Detection Settings
threshold = 25  # How Much pixel changes (default = 10)
sensitivity = 6  # How many pixels change (default = 100) # default = 20 if using a spotlight
streamWidth = 256  # motion scan stream Width
streamHeight = 128

####### SETUP ##########


def camera_setup(camera):
    camera.color_effects = (128, 128)  # grey shades
    camera.rotation = 180
    camera.resolution = (resolutionW, resolutionH)


camera = PiCamera()
camera_setup(camera)

def take():
    ### CAMERA ###
    camera_setup(camera)
    print ("Take a picture")
    timestamp = time.strftime("%Y%m%d%H%M%S")
    picFileName = ("testfoto"+"_"+timestamp+".jpg")
    camera.capture(picFileName)
    print ("Picture Taken!")  # See {0}_{1}.jpg!".format(set_name,timestamp)
    return picFileName


def crop(pictureFileName):
    ### PIC CROP ###
    print ("Crop the picture to the needed data")
    pic = Image.open(pictureFileName)
    pic.crop((cropX, cropY, cropX+cropResultWidth, cropY +
              cropResultHeight)).save(pictureFileName)
# ------------------------------------------------------------------------------

def get_stream_array():
    """ Take a stream image and return the image data array"""
    with picamera.array.PiRGBArray(camera) as stream:
#        camera.vflip = imageVFlip
 #       camera.hflip = imageHFlip
  #      camera.exposure_mode = 'auto'
   #     camera.awb_mode = 'auto'
        camera.rotation = 180
        camera.resolution = (streamWidth,streamHeight)
        camera.capture(stream, format='rgb')
        return stream.array

# ------------------------------------------------------------------------------

def saveMotionComparison():
    return get_stream_array()

def motion(comparison,maxChecks = 2):
    print ("Loop until motion is detected")
    i = 0
    data1 = comparison
    while i < maxChecks:
        data2 = get_stream_array()
        diff_count = 0
        for x in range(0, streamWidth):
            for y in range(0, streamHeight):
                # get pixel differences. Conversion to int
                # is required to avoid unsigned short overflow.
                diff = abs(int(data1[y][x][1]) - int(data2[y][x][1]))
                if diff > threshold:
                    diff_count += 1
                    print ("Threshold Difference: "+str(diff)+"  Senstivity Difference: "+str(diff_count))
                    if diff_count > sensitivity:
                        # x,y is a very rough motion position
                        # return x, y
                        print ("Detected Motion")
                        print ("Threshold Difference: "+str(diff)+"  Senstivity Difference: "+str(diff_count))
                        return True
        i += 1
        data1 = data2
    return False
