import boto3

def detect_text(photo, bucket="rasppicardscanner"):

    client=boto3.client('rekognition', region_name='eu-central-1') 
	# with Frankfurt = eu-central-1

    response=client.detect_text(Image={'S3Object':{'Bucket':bucket,'Name':photo}})
    textDetections=response['TextDetections']
    print ('Detected text\n----------')
    for text in textDetections:
            print ('Detected text:' + text['DetectedText'])
            print ('Confidence: ' + "{:.2f}".format(text['Confidence']) + "%")
            #print ('Id: {}'.format(text['Id']))
            #if 'ParentId' in text:
            #    print ('Parent Id: {}'.format(text['ParentId']))
            print ('Type:' + text['Type'])
            print()
	    if text['Type'] == 'LINE':
            	cardName=text['DetectedText']
    return cardName
