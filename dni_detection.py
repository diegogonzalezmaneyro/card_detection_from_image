#!/usr/bin/env python
"""Very simple card detection with OpenCV
"""

import base64
import cv2
import numpy as np

from io import BytesIO
from PIL import Image

def dni_from_image(base64_image):
    
    # load image from base64
    pil_image = Image.open(BytesIO(base64.b64decode(base64_image)))
    img_orig = np.asarray(pil_image)
    orig_HEIGHT, orig_WIDTH, _ = img_orig.shape

    # resize image and create a copy to handle
    WIDTH = 640
    HEIGHT = 400
    resized = cv2.resize(img_orig, (WIDTH,HEIGHT), interpolation=cv2.INTER_AREA )
    img = resized.copy()

    # resize scale
    W_scale = orig_WIDTH/WIDTH
    H_scale = orig_HEIGHT/HEIGHT
    
    # define some vars
    scale = 1
    delta = 0
    ddepth = cv2.CV_16S
    
    # image preprocessing to better get edges in image
    img_blur = cv2.GaussianBlur(img, (3, 3), 0)
    gray = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)

    # Gradient-X
    grad_x = cv2.Sobel(gray, ddepth, 1, 0, ksize=3, scale=scale, delta=delta, borderType=cv2.BORDER_DEFAULT)
    abs_grad_x = cv2.convertScaleAbs(grad_x)
    # Gradient-Y
    grad_y = cv2.Sobel(gray, ddepth, 0, 1, ksize=3, scale=scale, delta=delta, borderType=cv2.BORDER_DEFAULT)
    abs_grad_y = cv2.convertScaleAbs(grad_y)

    grad = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)
    
    # get upper limit
    y1_thresh = 150
    mask_y1 = np.zeros((HEIGHT,WIDTH))
    edges = cv2.Canny(grad[:y1_thresh],50,150,apertureSize = 3)

    lines = cv2.HoughLines(edges,1,np.pi/180,50)
    for rho,theta in lines[0]:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))
        cv2.line(mask_y1,(x1,y1),(x2,y2),(255,255,255),3)

    aux=np.where(mask_y1==255)
    crop_y1 = int(aux[0].mean())

    # get lower limit
    y2_thresh = 250
    mask_y2 = np.zeros((HEIGHT,WIDTH))
    edges = cv2.Canny(grad[y2_thresh:],50,150,apertureSize = 3)

    lines = cv2.HoughLines(edges,1,np.pi/180,50)
    for rho,theta in lines[0]:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))
        cv2.line(mask_y2,(x1,y2_thresh+y1),(x2,y2_thresh+y2),(255,255,255),3)
        
    aux=np.where(mask_y2==255)
    crop_y2 = int(aux[0].mean())
    
    # get left limit
    x1_thresh = 200
    mask_x1 = np.zeros((HEIGHT,WIDTH))
    edges = cv2.Canny(grad[:,:x1_thresh],50,150,apertureSize = 3)

    lines = cv2.HoughLines(edges,1,np.pi/180,50)
    for rho,theta in lines[0]:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))
        cv2.line(mask_x1,(x1,y1),(x2,y2),(255,255,255),3)
        
    aux=np.where(mask_x1==255)
    crop_x1 = int(aux[1].mean())
    
    #get right limit
    x2_thresh = 440
    mask_x2 = np.zeros((HEIGHT,WIDTH))
    edges = cv2.Canny(grad[:,x2_thresh:],50,150,apertureSize = 3)

    lines = cv2.HoughLines(edges,1,np.pi/180,50)
    for rho,theta in lines[0]:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))
        cv2.line(mask_x2,(x2_thresh+x1,y1),(x2_thresh+x2,y2),(255,255,255),3)
        
    aux=np.where(mask_x2==255)
    crop_x2 = int(aux[1].mean())
    
    ##################################################
    # crop = img[crop_y1:crop_y2, crop_x1:crop_x2,:]
    crop = img_orig[int(crop_y1*H_scale):int(crop_y2*H_scale),int(crop_x1*W_scale):int(crop_x2*W_scale),:]
    crop_image = Image.fromarray(crop)
    buffered = BytesIO()
    crop_image.save(buffered, format="png")
    crop_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    return crop_b64
