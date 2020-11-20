import os
import datetime
import time
import glob
from picamera import PiCamera
#import picamera
import picamera.array

camera = PiCamera()

def get_stream_array():
    """ Take a stream image and return the image data array"""
    camera.resolution = (streamWidth, streamHeight)
    with picamera.array.PiRGBArray(camera) as stream:
        camera.vflip = imageVFlip
        camera.hflip = imageHFlip
        camera.exposure_mode = 'auto'
        camera.awb_mode = 'auto'
        camera.capture(stream, format='rgb')
        camera.close()
        return stream.array

# ------------------------------------------------------------------------------


def motion():
    """ Loop until motion is detected """
    data1 = get_stream_array()
    while True:
        data2 = get_stream_array()
        diff_count = 0
        for y in range(0, streamHeight):
            for x in range(0, streamWidth):
                # get pixel differences. Conversion to int
                # is required to avoid unsigned short overflow.
                diff = abs(int(data1[y][x][1]) - int(data2[y][x][1]))
                if diff > threshold:
                    diff_count += 1
                    if diff_count > sensitivity:
                        # x,y is a very rough motion position
                        # return x, y
                        return True
        data1 = data2
