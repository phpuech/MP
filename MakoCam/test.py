    
from __future__ import absolute_import, print_function, division
# from pymba import *
import numpy as np
import cv2
import time
import os
import sys



x=800
y=600
z=1
image = np.zeros([int(x),int(y),int(z)],dtype=np.uint8)
deux = np.zeros([int(x),int(y),int(z)],dtype=np.uint8)
black = image.fill(255)
white = deux.fill(0)

print(deux)


whererepertoire='C:/Users/Pierre-Henri Puech/Desktop/'
nomrepertoire='SPEEDY'
# ----------------------------------------------------
repertoire=whererepertoire+nomrepertoire+'/'

if not os.path.exists(repertoire):
    os.makedirs(repertoire)

for i in np.arange(12):
	if i==0:
		final=image
	else:
		if i % 2 == 0:
			final=np.dstack((final, image))
		else:
			final=np.dstack((final, deux))
    


print(final.shape)
print(final)


print(final[:,:,3].shape)
print(final[:,:,3])

j=0
while j < 6:
    name=repertoire+'image'+str(j)+'.tiff'
    cv2.imwrite(name,final[:,:,3])
    

