# -*- coding: utf-8 -*-
"""
Created on Mon Jul 07 14:59:03 2014
@author: derricw
"""
# ----------------------------------------------------

from __future__ import absolute_import, print_function, division
from pymba import *
import numpy as np
import cv2
import time
import os
import sys
if sys.version_info[0] < 3: 
    from StringIO import StringIO
else:
    from io import StringIO
# ----------------------------------------------------
now = time.strftime("%c")
today =time.strftime("%Y")+time.strftime("%m")+time.strftime("%d")
heure = time.strftime("%H")+time.strftime("%M")+time.strftime("%S")
maintenant = today + "-" + heure
# ----------------------------------------------------
fps=380 #frames /sec MAKO U051B max = 391 theo, vrai 380
#interval=1 #sec
exposure=1 #msec BE CAREFUL
showevery=30 #frames
# ----------------------------------------------------
whererepertoire='C:/Users/Pierre-Henri Puech/Desktop/'
nomrepertoire='data'
nom='image'
timenom='frames'
# ----------------------------------------------------
repertoire=whererepertoire+maintenant+nomrepertoire+'/'
if not os.path.exists(repertoire):
    os.makedirs(repertoire)
# ----------------------------------------------------
#if interval !=0:
#    fps=1/interval
#else:
#    fps='NA'
# ----------------------------------------------------
print('on sauve ici')
print(repertoire)
print("on est partis pour", fps, "frames/sec...")
#print("intervalle", interval)
#print('image', exposure/1000)
#print('intervalle + image', interval+exposure/1000)
#duration=interval+exposure/1000
print('------------------------')
# ----------------------------------------------------

cv2.namedWindow("Type ESC to exit")

def blanck(x,y,z, *p):
        image = np.zeros([x,y,z],dtype=np.uint8)
        white = image.fill(255)
        return white


with Vimba() as vimba:
    system = vimba.getSystem()

    system.runFeatureCommand("GeVDiscoveryAllOnce")
    time.sleep(0.2)

    camera_ids = vimba.getCameraIds()

    for cam_id in camera_ids:
        print("Camera found: ", cam_id)
        
    c0 = vimba.getCamera(camera_ids[0])
    c0.openCamera()
#    try:
#        #gigE camera
#        print(c0.GevSCPSPacketSize)
#        print(c0.StreamBytesPerSecond)
#        c0.StreamBytesPerSecond = 100000000
#    except:
#        #not a gigE camera
#        pass


    print('Acquisition mode')
    print(c0.AcquisitionMode)
    c0.AcquisitionMode = 'Continuous' # 'MultiFrame', 'Continuous', 'SimpleFrame'
    print('Set to',c0.AcquisitionMode)
          
    print('Exposure time', c0.ExposureTime, 'microsec')
    c0.ExposureTime=exposure*1000
    print('Set to',c0.ExposureTime, 'microsec')
    
    print('Acquisition Frame Rate Mode', c0.AcquisitionFrameRateMode)
    c0.AcquisitionFrameRateMode='Basic'
    print('Set to', c0.AcquisitionFrameRateMode)
    print('Acquisition frame rate',c0.AcquisitionFrameRate)
    c0.AcquisitionFrameRate=fps
    print('Set to', c0.AcquisitionFrameRate)
    #set pixel format
    c0.PixelFormat="Mono8"
    #c0.ExposureTimeAbs=60000

    frame = c0.getFrame()
    frame.announceFrame()

    c0.startCapture()

    framecount = 0
    droppedframes = []

    stockageram={}
#    listetemps2=[]
    
#    t=0
    debut=time.clock()
    
    print("============================================")
    print("Running... press ESC to quit and save images")
    print("============================================")
    
    c0.runFeatureCommand("AcquisitionStart")
    frame.queueFrameCapture()
    
    while 1:
#        try:
#            frame.queueFrameCapture()
#            success = True
#        except:
#            droppedframes.append(framecount)
#            success = False
        
#        c0.runFeatureCommand("AcquisitionStart")
#        temps=c0.Timestamp
#        c0.runFeatureCommand("AcquisitionStop")
        
#        temps2=time.clock()
#        listetemps2.append(temps2)
        frame.waitFrameCapture(1000)#was set to a 1000
        tempsimage=c0.Timestamp
        if framecount==0:
            tempszero=tempsimage
            temps=0
        else:
            temps=np.round((tempsimage-tempszero)/10**6,1)
            
        try:
            frame.queueFrameCapture()
            success = True
        except:
            droppedframes.append(framecount)
            success = False
        frame_data = frame.getBufferByteData()
        if success:
            stockageram[temps]=np.ndarray(buffer=frame_data,
                	             dtype=np.uint8,
                	             shape=(frame.height,frame.width,1))
            if framecount % showevery == 0:
                cv2.imshow("Type ESC to exit",stockageram[temps])
                k = cv2.waitKey(1)
        else:
            stockageram[temps]=blanck(frame.height,frame.width,1)
        
        framecount+=1
        #k = cv2.waitKey(1)
        #♦time.sleep(interval)
        
        if k == 0x1b:
            fin=time.clock()
            cv2.destroyAllWindows()
            duration=fin-debut
            print("Frames stocked: %i"%framecount)
            print("Frame displayed: %i"%(framecount//showevery))
            print("Frames dropped: %s"%droppedframes)
            print("Duration", duration)
            print("Measured Frame Rate", framecount/duration)
            
            file = open(repertoire+timenom+'.txt', "w")
            file.write("# Date & Time: " +str(maintenant)+'\n')
            file.write("# Frames stocked: " +str(framecount)+'\n')
            file.write("# Frames dropped: " +str(droppedframes)+'\n')
            file.write("# Duration (sec): " +str(duration)+'\n')
            file.write("# Show every: " +str(showevery)+' th frame'+'\n')
            file.write("# fps Asked: " +str(fps)+'\n')          
            file.write("# fps Measure: " +str(framecount/duration)+'\n')  
#            file.write('# Exposure (msec): '+ str(exposure)+'\n')
#            file.write('# Interval (sec): '+str(interval)+'\n')
#            file.write("Frame Rate:", c0.AcquisitionFrameRate)
#            file.write('# Theoretical separation (sec): '+str(duration)+'\n')
#            file.write('# NumberStored Timestamp difference Temps2 difference\n')
            file.write('# ImageStored DeltaTime (msec)\n')
            j=0
            print("============================================")
            print("Saving... be patient...")
            print("============================================")
            for key in stockageram:
                if j==0:
                    keystart=key
                name=repertoire+nom+'-'+str(key)+'.tiff'
                cv2.imwrite(name,stockageram[key])
                file.write(str(j)+' '+str(key)+'\n')#" "+str(key-keystart)+" "+str(listetemps2[j])+" "+str(listetemps2[j]-listetemps2[0])+'\n')
                j+=1
            file.close()
            break
    print("Finished")
    print("============================================")
    
    c0.runFeatureCommand("AcquisitionStop")
    c0.endCapture()
    c0.revokeAllFrames()
    c0.closeCamera()