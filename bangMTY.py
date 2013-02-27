#! /usr/bin/env python

#import RPi.GPIO as GPIO
import time
import Queue
import pygame
from pygame.locals import *

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

## TODO: 
#  - TWITTER: https://github.com/tweepy/tweepy
#             https://github.com/ryanmcgrath/twython
#  - GPIO: http://bit.ly/RxbXd1 (adafruit example)
#          http://bit.ly/JTlFE3 (elinux.org wiki)
#  - GRAPHICS: http://bit.ly/96VoEC (pygame)


######### time constants
## how often to check twitter (in seconds)
TWITTER_CHECK_PERIOD = 10
## how often to check queue for new tweets to be processed (in seconds)
##     or, how much time between bang routines
QUEUE_CHECK_PERIOD = 10
## how long to keep motors on (in seconds)
MOTOR_ON_PERIOD = 0.5
## how long to keep each light on (in seconds)
LIGHT_ON_PERIOD = [1.0, 0.75]
## number of bangs per routine 
##     (this can be dynamic, based on length of tweet, for example)
NUMBER_OF_BANGS = 10

######### state machine
## different states motors can be in
STATE_WAITING, STATE_BANGING_FORWARD, STATE_BANGING_BACK = range(3)
## state/time variables
currentMotorState = STATE_WAITING
bangsLeft = 0
lastTwitterCheck = time.time()
lastMotorUpdate = time.time()
currentLightState = [False, False]
lastLightUpdate = [time.time(), time.time()]

## tweet queue
tweetQueue = Queue.Queue()

######### GPIO stuff
MOTOR_FWD = 17
MOTOR_BACK = 18
LIGHT_PIN = [22, 23]
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(MOTOR_FWD, GPIO.OUT)
#GPIO.setup(MOTOR_BACK, GPIO.OUT)
#GPIO.setup(LIGHT_PIN[0], GPIO.OUT)
#GPIO.setup(LIGHT_PIN[1], GPIO.OUT)
#GPIO.output(MOTOR_FWD, False)
#GPIO.output(MOTOR_BACK, False)
#GPIO.output(LIGHT_PIN[0], False)
#GPIO.output(LIGHT_PIN[1], False)

######### Windowing stuff
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Test')

background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((250, 250, 250))

screen.blit(background, (0, 0))
pygame.display.flip()


print "WAITING"

while True:
    ## handle events
    for event in pygame.event.get():
        if event.type == MOUSEBUTTONDOWN:
            tweetQueue.put("messaged!!!")

    ## twitter check. not needed if using streams
    if (time.time()-lastTwitterCheck > TWITTER_CHECK_PERIOD):
        # check twitter here
        # build queue
        lastTwitterCheck = time.time()

    ## state machine for motors
    ## if motor is idle, and there are tweets to process, start dance
    if ((currentMotorState==STATE_WAITING) and
        (time.time()-lastMotorUpdate > QUEUE_CHECK_PERIOD) and
        (not tweetQueue.empty())):
        print "BANG FWD"
        tweetText = tweetQueue.get()
        #   TODO: display message?
        #   GPIO.output(MOTOR_FWD, True)
        #   GPIO.output(MOTOR_BACK, False)
        currentMotorState=STATE_BANGING_FORWARD
        lastMotorUpdate = time.time()
        bangsLeft = NUMBER_OF_BANGS
    ## if motor0 has been on for a while, reverse it
    elif ((currentMotorState==STATE_BANGING_FORWARD) and
          (time.time()-lastMotorUpdate > MOTOR_ON_PERIOD) and
          (bangsLeft>0)):
        print "BANG BACK"
        #   GPIO.output(MOTOR_FWD, False)
        #   GPIO.output(MOTOR_BACK, True)
        currentMotorState=STATE_BANGING_BACK
        lastMotorUpdate = time.time()
        bangsLeft -= 1
    ## if motor1 has been on for a while, reverse it
    elif ((currentMotorState==STATE_BANGING_BACK) and
          (time.time()-lastMotorUpdate > MOTOR_ON_PERIOD) and
          (bangsLeft>0)):
        print "BANG FWD"
        #   GPIO.output(MOTOR_FWD, True)
        #   GPIO.output(MOTOR_BACK, False)
        currentMotorState=STATE_BANGING_FORWARD
        lastMotorUpdate = time.time()
    ## if no more bangs left
    elif((currentMotorState != STATE_WAITING) and 
         (bangsLeft <= 0) and 
         (time.time()-lastMotorUpdate > MOTOR_ON_PERIOD)):
        print "WAITING"
        #   GPIO.output(MOTOR_FWD, False)
        #   GPIO.output(MOTOR_BACK, False)
        #   GPIO.output(LIGHT_PIN[0], False)
        #   GPIO.output(LIGHT_PIN[1], False)
        currentMotorState=STATE_WAITING
        lastMotorUpdate = time.time()

    ## state machine for lights
    ## if banging, flicker the lights
    if (currentMotorState != STATE_WAITING):
        for i in range(0,2):
            if (time.time()-lastLightUpdate[i] > LIGHT_ON_PERIOD[i]):
                currentLightState[i] = not currentLightState[i]
                #   GPIO.output(LIGHT_PIN[i], False)
