#! /usr/bin/env python

#import RPi.GPIO as GPIO
import time
import Queue
import wx

## TODO: 
#  - TWITTER
#  - GPIO
#  - GRAPHICS: 
#  http://stackoverflow.com/questions/9705201/capturing-mouse-events-outside-wx-frame-in-python


######### time constants
## how often to check twitter (in seconds)
TWITTER_CHECK_PERIOD = 10
## how often to check queue for new tweets to be processed (in seconds)
##     or, how much time between bang routines
QUEUE_CHECK_PERIOD = 10
## how long to keep motors on (in seconds)
MOTOR_ON_PERIOD = 0.5
## number of bangs per routine 
##     (this can be dynamic, based on length of tweet, for example)
NUMBER_OF_BANGS = 10

## different states motors can be in
STATE_WAITING, STATE_BANGING_FORWARD, STATE_BANGING_BACK = range(3)

## state/time variables
currentState = STATE_WAITING
bangsLeft = 0
lastTwitterCheck = time.time()
lastMotorCheck = time.time()

## tweet queue
tweetQueue = Queue.Queue()

## GPIO stuff
#GPIO.setmode(GPIO.BCM)
#MOTOR_FWD = 18
#MOTOR_BACK = 23
#GPIO.setup(MOTOR_FWD, GPIO.OUT)
#GPIO.setup(MOTOR_BACK, GPIO.OUT)
#GPIO.output(MOTOR_FWD, False)
#GPIO.output(MOTOR_BACK, False)

print "WAITING"

##while True:
def motorLoop(event):
    global currentState, bangsLeft
    global lastTwitterCheck, lastMotorCheck, tweetQueue

    ## twitter check. not needed if using streams
    if (time.time()-lastTwitterCheck > TWITTER_CHECK_PERIOD):
        # check twitter here
        # build queue
        lastTwitterCheck = time.time()

    ## state machine for motors
    ## if motor is idle, and there are tweets to process, start dance
    if ((currentState==STATE_WAITING) and
        (time.time()-lastMotorCheck > QUEUE_CHECK_PERIOD) and
        (not tweetQueue.empty())):
        print "BANG FWD"
        tweetText = tweetQueue.get()
        #   TODO: display message?
        #   GPIO.output(MOTOR_FWD, True)
        #   GPIO.output(MOTOR_BACK, False)
        currentState=STATE_BANGING_FORWARD
        lastMotorCheck = time.time()
        bangsLeft = NUMBER_OF_BANGS
    ## if motor0 has been on for a while, reverse it
    elif ((currentState==STATE_BANGING_FORWARD) and
          (time.time()-lastMotorCheck > MOTOR_ON_PERIOD) and
          (bangsLeft>0)):
        print "BANG BACK"
        #   GPIO.output(MOTOR_FWD, False)
        #   GPIO.output(MOTOR_BACK, True)
        currentState=STATE_BANGING_BACK
        lastMotorCheck = time.time()
        bangsLeft -= 1
    ## if motor1 has been on for a while, reverse it
    elif ((currentState==STATE_BANGING_BACK) and
          (time.time()-lastMotorCheck > MOTOR_ON_PERIOD) and
          (bangsLeft>0)):
        print "BANG FWD"
        #   GPIO.output(MOTOR_FWD, True)
        #   GPIO.output(MOTOR_BACK, False)
        currentState=STATE_BANGING_FORWARD
        lastMotorCheck = time.time()
    ## if no more bangs left
    elif((currentState != STATE_WAITING) and 
         (bangsLeft <= 0) and 
         (time.time()-lastMotorCheck > MOTOR_ON_PERIOD)):
        print "WAITING"
        #   GPIO.output(MOTOR_FWD, False)
        #   GPIO.output(MOTOR_BACK, False)
        currentState=STATE_WAITING
        lastMotorCheck = time.time()


class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None)
        self.panel = wx.Panel(self)
        self.panel.BackgroundColour = wx.RED
        self.panel.Bind(wx.EVT_LEFT_UP, self.onClick)
        self.panel.Bind(wx.EVT_IDLE, motorLoop)

    def onClick(self, event):
        global tweetQueue
        self.panel.BackgroundColour = wx.GREEN
        tweetQueue.put("fofofofof")

app = wx.App()
frame = Frame()
frame.Show()
app.MainLoop()
