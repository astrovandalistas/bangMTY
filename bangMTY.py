#! /usr/bin/env python
# -*- coding: latin-1 -*-

## References:
#  - GPIO: http://bit.ly/JTlFE3 (elinux.org wiki)
#          http://bit.ly/QI8sAU (wiring pi)
#          http://bit.ly/MDEJVo (wiringpi-python)
#  - TWITTER: https://github.com/tweepy/tweepy
#             https://github.com/ryanmcgrath/twython
#  - GRAPHICS: http://bit.ly/96VoEC (pygame)
#              http://bit.ly/XmX8gA (display.set_mode)
#              http://bit.ly/Ld5NXV (auto-login)
#  - REGEXP: http://bit.ly/5UuJA (Py RegExp Testing Tool)

## TODO:
## - Limit tweets to 70 characters
## - add Main function ??

import os, sys, platform, time
import re
import Queue
import pygame
from pygame.locals import *
from twython import Twython

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

## import wiringpi lib if available
HAS_WIRINGPI = True
try:
    import wiringpi
except ImportError:
    HAS_WIRINGPI = False

## setup GPIO object (real or fake)
if (HAS_WIRINGPI):
    gpio = wiringpi.GPIO(wiringpi.GPIO.WPI_MODE_SYS)
else:
    # define fake gpio class with gpio.LOW, gpio.HIGH, gpio.digitalWrite, etc
    class Gpio(object):
        def __init__(self):
            self.LOW = False
            self.HIGH = True
            self.OUTPUT = 0
        def digitalWrite(self,pin=0, val=False):
            anEmptyStatement = ""
        def pinMode(self,pin=0, val=False):
            anEmptyStatement = ""
    gpio = Gpio()


######### GPIO pins
MOTOR_PIN = [17, 18]
LIGHT_PIN = [22, 23]

## for setting up the GPIO pins
def setUpGpio():
    os.system("gpio export "+str(MOTOR_PIN[0])+" out 2> /dev/null")
    os.system("gpio export "+str(MOTOR_PIN[1])+" out 2> /dev/null")
    os.system("gpio export "+str(LIGHT_PIN[0])+" out 2> /dev/null")
    os.system("gpio export "+str(LIGHT_PIN[1])+" out 2> /dev/null")

    gpio.pinMode(MOTOR_PIN[0],gpio.OUTPUT)
    gpio.pinMode(MOTOR_PIN[1],gpio.OUTPUT)
    gpio.pinMode(LIGHT_PIN[0],gpio.OUTPUT)
    gpio.pinMode(LIGHT_PIN[1],gpio.OUTPUT)

    gpio.digitalWrite(MOTOR_PIN[0],gpio.LOW)
    gpio.digitalWrite(MOTOR_PIN[1],gpio.LOW)
    gpio.digitalWrite(LIGHT_PIN[0],gpio.LOW)
    gpio.digitalWrite(LIGHT_PIN[1],gpio.LOW)

## for cleaning up the GPIO pins on exit
def cleanUpGpio():
    print "Cleaning up GPIO"
    gpio.digitalWrite(MOTOR_PIN[0],gpio.LOW)
    gpio.digitalWrite(MOTOR_PIN[1],gpio.LOW)
    gpio.digitalWrite(LIGHT_PIN[0],gpio.LOW)
    gpio.digitalWrite(LIGHT_PIN[1],gpio.LOW)


######### time constants
## how often to check twitter (in seconds)
TWITTER_CHECK_PERIOD = 10
## how often to check queue for new tweets to be processed (in seconds)
##     or, how much time between bang routines
QUEUE_CHECK_PERIOD = 1
## how long to keep motors on (in seconds)
MOTOR_ON_PERIOD = 0.5
## how long to wait between turning on motors (in seconds)
MOTOR_OFF_PERIOD = 0.3
## how long to keep each light on (in seconds)
LIGHT_ON_PERIOD = [0.25, 0.333]
## number of bangs per routine 
##     (this can be dynamic, based on length of tweet, for example)
NUMBER_OF_BANGS = 10
## font size (height in pixels)
FONT_SIZE = 210
## how long to keep text in same position before moving it (in seconds)
TEXT_SCROLL_PERIOD = 0.1

######### state machine
## different states motors can be in
(STATE_WAITING, STATE_BANGING_FORWARD, STATE_BANGING_BACK, 
 STATE_PAUSE_FORWARD, STATE_PAUSE_BACK) = range(5)
## state/time variables
currentMotorState = STATE_WAITING
bangsLeft = 0
currentLightState = [False, False]
lastTwitterCheck = time.time()
lastMotorUpdate = time.time()
lastLightUpdate = [time.time(), time.time()]
lastTextUpdate = time.time()

## tweet queue
tweetQueue = Queue.Queue()

######### twitter init
twitter = None
twitterAuthenticated = False
twitterResults = None
## get tweets that come after this
## a post by @LemurLimon on 2013/02/23
largestTweetId = 305155172542324700
tweetSplit = re.compile("^(.{0,70}) (.{0,70})$")
## with these terms
SEARCH_TERM = "#bangMTY #BangMTY #bangMty #BangMty #bangmty #Bangmty #BANGMTY"

## read secrets from file
inFile = open('oauth.txt', 'r')
secrets = {}
for line in inFile:
    (k,v) = line.split()
    secrets[k] = v

## parse results and get largest Id for tweets that came before running the program
def getLargestTweetId():
    global largestTweetId
    if (not twitterResults is None):
        for tweet in twitterResults["statuses"]:
            print ("Tweet %s from @%s at %s" % 
                   (tweet['id'],
                    tweet['user']['screen_name'],
                    tweet['created_at']))
            print tweet['text'],"\n"
            if (int(tweet['id']) > largestTweetId):
                largestTweetId = int(tweet['id'])

## authenticate
def authenticateTwitter():
    global twitter, twitterAuthenticated
    try:
        twitter = Twython(twitter_token = secrets['CONSUMER_KEY'],
                          twitter_secret = secrets['CONSUMER_SECRET'],
                          oauth_token = secrets['ACCESS_TOKEN'],
                          oauth_token_secret = secrets['ACCESS_SECRET'])
        twitterAuthenticated = True
        ## assume connected
        searchTwitter()
        getLargestTweetId()
    except:
        twitter = None
        twitterAuthenticated = False

## query twitter
def searchTwitter():
    global twitterResults
    if ((not twitterAuthenticated) or (twitter is None)):
        authenticateTwitter()
    try:
        twitterResults = twitter.search(q=SEARCH_TERM, include_entities="false",
                                       count="50", result_type="recent",
                                       since_id=largestTweetId)
    except:
        twitterResults = None


######### Windowing stuff
screen = None
background = None
font = None
textAndPos = None

def setUpWindowing():
    global screen, background, font, textAndPos

    flags = pygame.FULLSCREEN|pygame.DOUBLEBUF|pygame.HWSURFACE

    pygame.init()
    screen = pygame.display.set_mode((0, 0),flags)
    pygame.display.set_caption('#bangMTY')
    pygame.mouse.set_visible(False)

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0,0,0))

    font = pygame.font.Font("./otis.ttf", FONT_SIZE)
    textAndPos = [{'text':font.render("", 1, (250,0,0)),
                   'pos':Rect(-2,0,-1,0)}]
    screen.blit(background, (0, 0))
    pygame.display.flip()

####### DEBUG
foo = "Calculate and display the number of characters within a TEXTAREA with this script."
s = time.time()
r = tweetSplit.search(foo)
print time.time()-s
for l in r.groups():
    print "len("+l+")="+str(len(l))

##sys.exit(0)


######### The Loop!!
try:
    setUpGpio()
    setUpWindowing()
    searchTwitter()
    print "WAITING"
    while True:
        loopStart = time.time()
        ## handle events
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                tweetQueue.put("MÉSSÃGÉD !!!")
            elif ((event.type == QUIT) or
                  (event.type == KEYDOWN and event.key == K_ESCAPE)):
                cleanUpGpio()
                sys.exit()

        ## blit stuff
        if ((textAndPos[0]['pos'].right > -1) and
            (time.time()-lastTextUpdate > TEXT_SCROLL_PERIOD)):
            background.fill((0,0,0))
            for tpd in textAndPos:
                tpd['pos'].right -= FONT_SIZE/7
                background.blit(tpd['text'], tpd['pos'])

            screen.blit(background, (0,0))
            pygame.display.flip()
            lastTextUpdate = time.time()

        ## twitter check.
        if ((currentMotorState==STATE_WAITING) and
            (time.time()-lastTwitterCheck > TWITTER_CHECK_PERIOD) and
            (textAndPos[0]['pos'].right < 0)):
            # check twitter
            searchTwitter()
            ## parse results, print stuff, push on queue
            if (not twitterResults is None):
                for tweet in twitterResults["statuses"]:
                    ## print
                    print ("pushing %s from @%s" %
                           (tweet['text'],
                            tweet['user']['screen_name']))
                    ## push
                    tweetQueue.put(tweet['text'])
                    ## update largestTweetId for next searches
                    if (int(tweet['id']) > largestTweetId):
                        largestTweetId = int(tweet['id'])
            
            ## update timer
            lastTwitterCheck = time.time()
    
        ## state machine for motors
        ## if motor is idle, no text is scrolling and there are 
        ##     tweets to process, then start dance
        if ((currentMotorState==STATE_WAITING) and
            (time.time()-lastMotorUpdate > QUEUE_CHECK_PERIOD) and
            (textAndPos[0]['pos'].right < 0) and
            (not tweetQueue.empty())):
            print "BANG FWD"
            tweetText = tweetQueue.get()
            # display message
            textAndPos[0]['text'] = font.render(tweetText, 1, (250,0,0))
            textAndPos[0]['pos'] = textAndPos[0]['text'].get_rect(
                left=background.get_width(), centery=background.get_height()/2)
            ### background.blit(text, textPos)
            # set pins
            gpio.digitalWrite(MOTOR_PIN[0],gpio.HIGH)
            gpio.digitalWrite(MOTOR_PIN[1],gpio.LOW)
            currentMotorState=STATE_BANGING_FORWARD
            lastMotorUpdate = time.time()
            bangsLeft = NUMBER_OF_BANGS
        ## if motor0 has been on for a while, pause, then reverse direction
        elif ((currentMotorState==STATE_BANGING_FORWARD) and
              (time.time()-lastMotorUpdate > MOTOR_ON_PERIOD) and
              (bangsLeft > 0)):
            gpio.digitalWrite(MOTOR_PIN[0],gpio.LOW)
            gpio.digitalWrite(MOTOR_PIN[1],gpio.LOW)
            currentMotorState=STATE_PAUSE_BACK
            lastMotorUpdate = time.time()            
        ## if we're done pausing, proceed
        elif ((currentMotorState==STATE_PAUSE_BACK) and
              (time.time()-lastMotorUpdate > MOTOR_OFF_PERIOD) and
              (bangsLeft > 0)):
            print "BANG BACK"
            gpio.digitalWrite(MOTOR_PIN[0],gpio.LOW)
            gpio.digitalWrite(MOTOR_PIN[1],gpio.HIGH)
            currentMotorState=STATE_BANGING_BACK
            lastMotorUpdate = time.time()
            bangsLeft -= 1
        ## if motor1 has been on for a while, pause, then reverse direction
        elif ((currentMotorState==STATE_BANGING_BACK) and
              (time.time()-lastMotorUpdate > MOTOR_ON_PERIOD) and
              (bangsLeft > 0)):
            gpio.digitalWrite(MOTOR_PIN[0],gpio.LOW)
            gpio.digitalWrite(MOTOR_PIN[1],gpio.LOW)
            currentMotorState=STATE_PAUSE_FORWARD
            lastMotorUpdate = time.time()            
        ## if we're done pausing, proceed
        elif ((currentMotorState==STATE_PAUSE_FORWARD) and
              (time.time()-lastMotorUpdate > MOTOR_OFF_PERIOD) and
              (bangsLeft > 0)):
            print "BANG FWD"
            gpio.digitalWrite(MOTOR_PIN[0],gpio.HIGH)
            gpio.digitalWrite(MOTOR_PIN[1],gpio.LOW)
            currentMotorState=STATE_BANGING_FORWARD
            lastMotorUpdate = time.time()
        ## if no more bangs left
        elif((currentMotorState != STATE_WAITING) and 
             (bangsLeft <= 0) and 
             (time.time()-lastMotorUpdate > MOTOR_ON_PERIOD)):
            print "WAITING"
            gpio.digitalWrite(MOTOR_PIN[0],gpio.LOW)
            gpio.digitalWrite(MOTOR_PIN[1],gpio.LOW)
            gpio.digitalWrite(LIGHT_PIN[0],gpio.LOW)
            gpio.digitalWrite(LIGHT_PIN[1],gpio.LOW)
            currentMotorState=STATE_WAITING
            lastMotorUpdate = time.time()
    
        ## state machine for lights
        ## if banging, flicker the lights
        if (currentMotorState != STATE_WAITING):
            for i in range(0,2):
                if (time.time()-lastLightUpdate[i] > LIGHT_ON_PERIOD[i]):
                    currentLightState[i] = not currentLightState[i]
                    gpio.digitalWrite(LIGHT_PIN[i],currentLightState[i])
                    lastLightUpdate[i] = time.time()
        ## keep it from looping faster than ~60 times per second
        loopTime = time.time()-loopStart
        if loopTime < 0.017:
            time.sleep(0.017 - loopTime)

except KeyboardInterrupt:
    cleanUpGpio()

