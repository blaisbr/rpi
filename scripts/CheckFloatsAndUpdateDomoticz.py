#!/usr/bin/env python

import urllib2
import json
import RPi.GPIO as GPIO
import time

# The dictionnary FLOATS contains all the relation between a GPIO pin and a Domoticz index. 
# The key is the gpio pin board number
# The value is the domotics device index number

FLOATS = {37: 23, 35: 24, 33: 25, 31: 26, 29: 27}

def manageFloat(idPin):
	idDomoticz = FLOATS[idPin] #Extract the domoticz idx from the dictionnary
        pinValue = GPIO.input(idPin) # 1 = the float is up (under water), 0 = the float is down (outside water)
        jsonFragment = json.load(urllib2.urlopen("http://192.168.0.4:8080/json.htm?type=devices&rid=%d"%idDomoticz))
        domoticzValue = jsonFragment['result'][0]['Data'] # On|Off = the switch status
	print ("ManageFloat: gpio {} = {}  - domoticz idx {} = {}".format(idPin, pinValue, idDomoticz, domoticzValue))
        if pinValue == 1:
                if domoticzValue == 'Off':
			print ("Switch on the float component on Domoticz")
                        urllib2.urlopen("http://192.168.0.4:8080/json.htm?type=command&param=switchlight&idx=%d&switchcmd=On"%idDomoticz)
        else:
                if domoticzValue == 'On':
                        print ("Switch off the float component on Domoticz")
                        urllib2.urlopen("http://192.168.0.4:8080/json.htm?type=command&param=switchlight&idx=%d&switchcmd=Off"%idDomoticz)


try:
	GPIO.setmode(GPIO.BOARD)
	for k in FLOATS.iterkeys():
		print "Set the gpio %d in input mode"%k
		GPIO.setup(k, GPIO.IN)
		manageFloat(k)
		GPIO.add_event_detect(k, GPIO.BOTH, callback=manageFloat)

except RuntimeError as e:
  GPIO.cleanup()
  print e
  exit_msg = "Bombing out after setup"
  raise SystemExit, exit_msg

try:
  while True:
    time.sleep(3600) # Go to bed for 1 hour, don't worry domoticz will be updated if an event is detected on the gpio pins!
except KeyboardInterrupt:
    GPIO.cleanup()
