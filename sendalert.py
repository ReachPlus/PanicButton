import thread
import json
import RPi.GPIO as GPIO
from time import sleep

import requests
from requests.auth import HTTPBasicAuth

flag = 1

def setupGPIO( ):
    GPIO.setmode(GPIO.BOARD)     # set up BOARD GPIO numbering
    GPIO.setup(sendStatusPin, GPIO.OUT)    # set GPIO as an output (LED)
    GPIO.setup(systemOnlinePin, GPIO.OUT)    # set GPIO as an output (LED)
    GPIO.setup(triggerInputPin, GPIO.IN,  pull_up_down=GPIO.PUD_DOWN)   # set GPIO triggerInputPin as input (button)

def transmitError( ):
    for x in range(0, 15):
        GPIO.output(sendStatusPin,0)
        sleep(1)
        GPIO.output(sendStatusPin,1)
        sleep(1)

def systemError( ):
    for x in range(0, 60):
        GPIO.output(systemOnlinePin,0)
        sleep(1)
        GPIO.output(systemOnlinePin,1)
        sleep(1)


def sendAlert( ):

    #Alert
    with open (alertSampleFile, "r") as myfile:
        alertPalyload=myfile.read().replace('\n', '')

    #sending
    try:
        headers = {'Content-type': 'application/xml', 'Accept': 'text/plain'}
        result = requests.post(sdkUrl, data=alertPalyload , auth=HTTPBasicAuth(rpasUser, rpasPassword), headers=headers)
        print "Alert sent successfully"
        print (result.text)
        sleep(30)
    except:	
        print "Failed sending alert"
        transmitError()


def sendAlertThread( ):
    try:
        while True:            # this will carry on until you hit CTRL+C
            if GPIO.input(triggerInputPin): # if port triggerInputPin == 1
               # print " LED ON"
                GPIO.output(sendStatusPin, 1)         # set port/pin value to 1/HIGH/True
                if flag:
                    flag = 0
                print "Sending alert"
                try:
                    sendAlert()
                finally:
                    GPIO.output(sendStatusPin,0)

            else:
                GPIO.output(sendStatusPin, 0)         # set port/pin value to 0/LOW/False
                flag = 1

            sleep(0.1)         # wait 0.1 seconds

    finally:                   # this block will run no matter how the try block exits
        GPIO.cleanup()         # clean up after yourself


def onlineBlinkerThread( ):
    try:
        while True:            # this will carry on until you hit CTRL+C

            GPIO.output(systemOnlinePin, 1) # set port/pin value to 1/HIGH/True
            sleep(2)           # wait 0.1 seconds

    finally:                   # this block will run no matter how the try block exits
        GPIO.cleanup()         # clean up after yourself
        systemError()


with open('settings.config.json') as json_data_file:
    config = json.load(json_data_file)

sdkUrl = config['settings']['sdkUrl']
rpasUser = config['settings']['rpasUser']
rpasPassword = config['settings']['rpasPassword']
triggerInputPin = config['settings']['triggerInputPin']
systemOnlinePin = config['settings']['systemOnline']
sendStatusPin = config['settings']['sendStatus']
alertSampleFile = config['settings']['alertSampleFile']

setupGPIO ()

GPIO.output(systemOnlinePin, 0)
GPIO.output(sendStatusPin, 0)
try:
   thread.start_new_thread( onlineBlinkerThread, ( ) )
   thread.start_new_thread( sendAlertThread, ( ) )
except:
   print "Error: unable to start thread"
   systemError()


GPIO.output(systemOnlinePin, 1)
GPIO.output(sendStatusPin, 1)

while 1:
   pass
