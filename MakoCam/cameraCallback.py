# -*- coding: utf-8 -*-
 
from pymba import *
import time, Queue
import numpy as np
 
 
def frame_cb(frame):
    print("Start Callback {} with Frame {}".format(str(frame_cb), str(frame)))
    img = np.ndarray(buffer=frame.getBufferByteData(),
                     dtype=np.uint8,
                     shape=(frame.height, frame.width))
    frame.queueFrameCapture(frame_cb)
    print("End Callback {} with Frame {}".format(str(frame_cb), str(frame)))
 
 
def test_frame_callback():
    # start Vimba
    vimba = Vimba()
    vimba.startup()
 
    # get system object
    system = vimba.getSystem()
 
    # list available cameras (after enabling discovery for GigE cameras)
    if system.GeVTLIsPresent:
        system.runFeatureCommand("GeVDiscoveryAllOnce")
        time.sleep(0.2)
    cameraIds = vimba.getCameraIds()
 
    # get and open a camera
    camera0 = vimba.getCamera(cameraIds[0])
    camera0.openCamera()
 
    # set the value of a feature
    camera0.AcquisitionMode = 'Continuous'
 
    # get ready to capture
    camera0.startCapture()
 
    # create new frames for the camera
    frames = [camera0.getFrame() for _ in xrange(2)]
 
    for frame in frames:
        print("Created Frame {}, Struct {}".format(str(frame), str(frame._frame)))
 
    # announce and queue frames
    for frame in frames:
        frame.announceFrame()
        frame.queueFrameCapture(frameCallback=frame_cb)
 
    # capture some images
    run_duration = 10.0 # seconds
    camera0.runFeatureCommand('AcquisitionStart')
    time.sleep(run_duration)
    camera0.runFeatureCommand('AcquisitionStop')
    time.sleep(0.5)
 
    # clean up after capture
    camera0.endCapture()
    camera0.revokeAllFrames()
 
    # close camera
    camera0.closeCamera()
 
    # shutdown Vimba
    vimba.shutdown()
 
test_frame_callback()