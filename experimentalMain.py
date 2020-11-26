########### Some Experimental code lines

import logging
import boto3
from botocore.exceptions import ClientError
import glob, os
import sys
import scrython

######################## Constants #############################
awsUploadEnabled = False
SET_CODE = 'cmr'

######################## Functions #############################

def lineToTextfile(line, filename='MagicCardList.txt'):
    file = open(filename, "a")
    file.write("%s\n" % line)
    file.close()

def upload_file(file_name, bucket="rasppicardscanner", object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def detect_text(photo, bucket="rasppicardscanner"):
    cardName = ""
    client = boto3.client('rekognition', region_name='eu-central-1')
    # with Frankfurt = eu-central-1

    response = client.detect_text(
        Image={'S3Object': {'Bucket': bucket, 'Name': photo}})
    textDetections = response['TextDetections']
    print ('Detected text\n----------')
    for text in textDetections:
        print ('Detected text:' + text['DetectedText'])
        print ('Confidence: ' + "{:.2f}".format(text['Confidence']) + "%")
        #print ('Id: {}'.format(text['Id']))
        # if 'ParentId' in text:
        #    print ('Parent Id: {}'.format(text['ParentId']))
        print ('Type:' + text['Type'])
        print()
        if text['Type'] == 'LINE' and text['DetectedText']:
            cardName = text['DetectedText']
            lineToTextfile(cardName,"Lines.txt")

def addCard(card):
    price = ("Price N/A" if card.prices('eur') is None else (card.prices('eur') + " EUR "))
    print (card.name() + " | " + price)
    lineToTextfile(card.name())
    lineToTextfile("1x "+card.name()+" ("+SET_CODE.upper()+")","TappedoutList.txt")

def requestCard(fuzzycardname,setFilter=SET_CODE):
    try:
        card = scrython.cards.Named(fuzzy=str(fuzzycardname),set=setFilter)
        return card
    except Exception:
        return None

#########################Start of Main#####################################


if awsUploadEnabled:
    print ("Searching for JPEGs")
    for file in glob.glob("*.jpeg"):
        print ("Uploading" + str(file))
        upload_file(file)
        print ("Detecting Text")
        detect_text(file)

lastFoundCard = ""
previousLine = "" 
previousFound = True

file = open('Lines.txt')
for line in file:
    linecontent=line.rstrip()
    card = requestCard(linecontent)
    if card is None:
        card = requestCard(previousLine + linecontent)
        if card is None:
            card = requestCard(linecontent + previousLine)
            if card is None:
                print ("--- Not Found by API: "+str(linecontent))
                continue
    if (card.set_code() == SET_CODE):
        if (card.name() == lastFoundCard):
            print ("--- ignored assuming unwanted duplicate of: "+card.name())
        else:
            addCard(card)
            lastFoundCard = card.name()
    previousLine = linecontent
file.close()
