import numpy as np
import cv2
#import pytesseract
from matplotlib import pyplot as plt

def bw(image,th): #binary threshold an image
    bw_im = image>th
    return np.uint8(bw_im)
    
def bilateral_filter(im,d,sColor,sSpace):
    return cv2.bilateralFilter(im,d,sColor,sSpace)
"""
def read_scale(im,pa):
    im_get_temp = bw(im,250) #Threshold black white makes pytesseract readings more accurate
    
    temp_hi = pytesseract.image_to_string(im_get_temp[:pa.HIGH_BOT,pa.SCALE_LEFT:pa.SCALE_RIGHT])
    for idx in range(len(temp_hi)):
        if temp_hi[idx] not in pa.numbers:
            temp_hi = int(temp_hi[:idx])
            break
    #plt.figure()
    #plt.subplot(211)
    #plt.imshow(im_get_temp[pa.LOW_TOP:,pa.SCALE_LEFT:pa.SCALE_RIGHT],cmap='gray')
    #plt.subplot(212)
    #plt.imshow(im_get_temp[:pa.HIGH_BOT,pa.SCALE_LEFT:pa.SCALE_RIGHT],cmap='gray')
    #plt.close()
    print (pytesseract.image_to_string(im_get_temp[:pa.HIGH_BOT,pa.SCALE_LEFT:pa.SCALE_RIGHT]))
    print (pytesseract.image_to_string(im_get_temp[pa.LOW_TOP:,pa.SCALE_LEFT:pa.SCALE_RIGHT]))
    temp_low = pytesseract.image_to_string(im_get_temp[pa.LOW_TOP:,pa.SCALE_LEFT:pa.SCALE_RIGHT])
    for idx in range(len(temp_low)):
        if temp_low[idx] not in pa.numbers:
            temp_low = int(temp_low[:idx])
            break
        
    return temp_low,temp_hi
"""
def grayscale_to_temp(im,low,hi):
    print (low,hi)
    return im.astype(float)/255*(hi-low) + low

def resize(im,width,height):
    return cv2.resize(im,(width,height))

def denoise(im,templateWindowSize,searchWindowSize,h):
    return cv2.fastNlMeansDenoising(im,None,templateWindowSize,searchWindowSize,h) 

def dilate(im,kernel,iterations):
    return cv2.dilate(im,kernel,iterations=iterations)

def erode(im,kernel,iterations):
    return cv2.erode(im,kernel,iterations=iterations)

def outline_leak(im,minn,maxx):
    outline = cv2.Canny(im,minn,maxx)
    
    for i in range(1):
        for j in range(im.shape[0]):
            outline[j][i] = im[j][i]
            outline[j][-i-1] = im[j][-i-1]
        for j in range(im.shape[1]):
            outline[i][j] = im[i][j]
            outline[-i-1][j] = im[-i-1][j]
    
    return outline
    
def find_threshold(door_image):
    min_temp = np.min(door_image)
    max_temp = np.max(door_image)
    pixels = door_image.size #number of pixels
    min_T = min_temp + (max_temp-min_temp)*2/3 #We try threshold temperatures until min_T
    avg = np.uint8(np.average(door_image))
    
    door_image[door_image<avg] = avg #Truncate values below average

    threshold = max_temp-1
    best_var = 999999   
    best_T = threshold
    
    while(threshold > min_T):
        over = door_image > threshold
        under = door_image <= threshold
        
        over = door_image[over]
        under = door_image[under]
        
        if over.size==0 or under.size==0: #Empty set, should terminate
            threshold-=1
            continue #break
        
        #evaluate effectiveness of threshold values using within class variances 
        w_over,var_over = over.size/pixels,np.var(over)
        w_under,var_under = under.size/pixels,np.var(under)
        
        #class_var = w_over*w_under*(mean_over-mean_under)**2
        class_var = w_over + var_over + w_under * var_under
        
        #We are trying to minimize in-class variance
        if class_var < best_var:
            best_var = class_var
            best_T = threshold
        
        threshold -=1
        
    return best_T,best_var



