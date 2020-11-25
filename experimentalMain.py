########### Some Experimental code lines

import logging
import boto3
from botocore.exceptions import ClientError
import glob, os
import sys
import scrython

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

#########################Start of Main#####################################

print ("Searching for JPEGs")
for file in glob.glob("*.jpeg"):
    print ("Uploading" + str(file))
    upload_file(file)
    print ("Detecting Text")
    detect_text(file)

lastFoundCard = ""
file = open('Lines.txt')
for line in file:
    try:
        card = scrython.cards.Named(fuzzy=str(line.rstrip()))
        if (card.set_code() == 'cmr'):
            if (card.name() == lastFoundCard):
                print ("--- ignored assuming unwanted duplicate of: "+card.name())
            else:
                if float(card.prices('eur')) > 10:
                    print ("*** NICE HIT ***")
                print (card.name() + " | " + card.prices('eur') + " EUR ")
                lineToTextfile(card.name())
                lastFoundCard = card.name()
        else: 
            print ("Not in commander Set: " +card.name() + " instead in Sets: ")
            data = scrython.cards.Search(q="++{}".format(card.name()))
            for card in data.data():
                print ("    "+card['set'].upper(), ":", card['set_name'])
    except Exception:
        print ("--- Not Found by API: "+str(line.rstrip()))
   
file.close()