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
fps=10 #frames /sec MAKO U051B max = 391 theo, vrai 380 - optimal 350
exposure=35 #msec BE CAREFUL : 1 or 2 msec (3 does not work for fps 380)
showevery=2 #frames : fps/10 au min, 100 c'est mieux
# FROM PHP TESTS 180322
# optimisation : fps 380 expo 2 show 100 => 330 - 350 measured fps
# ----------------------------------------------------
whererepertoire='C:/Users/Pierre-Henri Puech/Desktop/'
nomrepertoire='SPEEDY'
nom='image'
timenom='frames'
# ----------------------------------------------------
repertoire=whererepertoire+nomrepertoire+'-'+maintenant+'/'
finalrepertoire=repertoire+'/final/'
if not os.path.exists(repertoire):
    os.makedirs(repertoire)
if not os.path.exists(finalrepertoire):
    os.makedirs(finalrepertoire)
# ----------------------------------------------------
print('on sauve ici')
print(repertoire)
print("on est partis pour", fps, "frames/sec...")
print('------------------------')
# ----------------------------------------------------

cv2.namedWindow("Type ESC to exit")

def blanck(x,y,z,grey, *p):
        image = np.zeros([x,y,z],dtype=np.uint8)
        white = image.fill(int(grey))
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

    frame = c0.getFrame()
    frame.announceFrame()

    c0.startCapture()

    framecount = 0
    droppedframes = []

    #stockageram={}
    stockageram=[]
    imagenumber=[]
    imagetemps=[]

    debut=time.clock()
    
    print("============================================")
    print("Running... press ESC to quit and save images")
    print("============================================")
    
    c0.runFeatureCommand("AcquisitionStart")
    frame.queueFrameCapture()
    
    whiteall=blanck(int(frame.height),int(frame.width),1,255)
    
    d=512
    white=blanck(int(d),int(d),1,255)
    black=blanck(int(d),int(d),1,0)
    
    while 1:

        frame.waitFrameCapture()#was set to a 1000
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
            image=np.ndarray(buffer=frame_data,
                	             dtype=np.uint8,
                	             shape=(frame.height,frame.width,1))
            cv2.putText(image,str(temps)+' msec', (int(25), int(50)),cv2.FONT_HERSHEY_SIMPLEX, 1, 255,2, cv2.LINE_AA)
            namestock=repertoire+nom+'-'+str(framecount)+'.tiff'
            cv2.imwrite(namestock,image)
            #print(type(image))
            if framecount % showevery == 0:
                cv2.imshow("Type ESC to exit",image)
                k = cv2.waitKey(1)
        else:
            image=whiteall
        #stockageram[temps]=image
        if framecount%2==0:
            image2=white#np.array([[0,0],[0,0]])
        else:
            image2=black#np.array([[255,255],[255,255]])
        stockageram.append(image)
        imagenumber.append(framecount)
        imagetemps.append(temps)
        
        framecount+=1
        
        if k == 0x1b:
            fin=time.clock()
            cv2.destroyAllWindows()
            break
        
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
    file.write('# ImageStored DeltaTime (msec)\n')
    
    print("============================================")
    print("Closing Camera...")
    print("============================================")
    
    c0.runFeatureCommand("AcquisitionStop")
    c0.endCapture()
    c0.revokeAllFrames()
    c0.closeCamera()
    
    print("Saving, be patient...")
    print("============================================")
    
    j=0
    #for key in stockageram:
    l=len(imagenumber)
    l2=len(stockageram)
    print('Saving', l2, 'images')
    while j<l:
        name=finalrepertoire+nom+'-'+str(imagenumber[j])+'.tiff'
        print(j, nom+'-'+str(imagenumber[j])+'.tiff')
        tracer=np.ndarray(buffer=stockageram[j],
                	             dtype=np.uint8,
                	             shape=(frame.height,frame.width,1) )
        print(type(tracer))
        cv2.imwrite(name,tracer)
        #time.sleep(0.5)
        file.write(str(imagenumber[j])+' '+str(imagetemps[j])+'\n')
        j+=1
    file.close()
    #        break
    print("Finished")
    print("============================================")
    
#    c0.runFeatureCommand("AcquisitionStop")
#    c0.endCapture()
#    c0.revokeAllFrames()
#    c0.closeCamera()