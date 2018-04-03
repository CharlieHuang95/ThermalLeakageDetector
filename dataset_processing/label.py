import cv2
import matplotlib.pyplot as plt
import numpy as np
import pytesseract
import time

im = None
SCALE_LEFT = 34
SCALE_RIGHT = 127
HI_BOT = 32
LOW_TOP = 1249
GRAYSCALE_CAP = 255
numbers = "-0123456789"
threshold_step = 0.1

def find_threshold(door_image):
    min_temp = np.min(door_image)
    max_temp = np.max(door_image)
    pixels = door_image.size #number of pixels
    min_T = min_temp + (max_temp-min_temp)*2/3 #We try threshold temperatures until min_T
    avg = np.uint8(np.average(door_image))
    
    door_image[door_image<avg] = avg #Truncate values below average
    
    #plt.figure()
    #plt.imshow(door_image,cmap='gray')

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
        w_over,mean_over,var_over = over.size/pixels,np.average(over),np.var(over)
        w_under,mean_under,var_under = under.size/pixels,np.average(under),np.var(under)
        
        #class_var = w_over*w_under*(mean_over-mean_under)**2
        class_var = w_over + var_over + w_under * var_under
        
        #print(threshold,class_var)
        
        #We are trying to minimize in-class variance
        if class_var < best_var:
            best_var = class_var
            best_T = threshold
        
        threshold -=1
        
    return best_T,best_var

def bw(image,th): #binary threshold an image
    bw_im = image>th
    bw_im = np.uint8(bw_im)
    #plt.imshow(bw_im,cmap='gray')
    
    return bw_im
    
def label(img_path,doorX1,doorX2,doorY1,doorY2,im_name="example"):
    #Door X,Y specify bounding box of door within the original image
    
    im = cv2.imread(img_path,0)
    #plt.imshow(im,cmap='gray')
    
    ##### Denoise image###########
    im_denoised = cv2.bilateralFilter(im,9,150,150) 
    
    comp = np.concatenate((im,im_denoised),axis=1)
    cv2.imwrite("denoised.jpg", comp)
    
    im = im_denoised
    
    ##### Read temperature scales #####
    im_get_temp = bw(im,200) #Threshold black white makes pytesseract readings more accurate
    
    temp_hi = pytesseract.image_to_string(im_get_temp[:HI_BOT,SCALE_LEFT:SCALE_RIGHT])
    print (temp_hi)
    for idx in range(len(temp_hi)):
        if temp_hi[idx] not in numbers:
            temp_hi = int(temp_hi[:idx])
            break
    
    plt.imshow(im_get_temp[LOW_TOP:,SCALE_LEFT:SCALE_RIGHT],cmap='gray')
    temp_low = pytesseract.image_to_string(im_get_temp[LOW_TOP:,SCALE_LEFT:SCALE_RIGHT])
    #print(temp_low)
    
    for idx in range(len(temp_low)):
        if temp_low[idx] not in numbers:
            temp_low = int(temp_low[:idx])
            break
    
    #print(temp_low,temp_hi)
    
    ##### Downsize image ######
    downsized_og = cv2.resize(im,(156,206))
    downsized_og = cv2.fastNlMeansDenoising(downsized_og,None,5,7,21) #Denoise
    
    temp_range = temp_hi-temp_low
    
    ##### Translate pixel values into temperature values #####
    #openCV functions performed on pixel values, but we can use temperature values to evaluate if 
    #labeled area is significant
    img_temperature = np.zeros((206,156))#-SCALE_RIGHT))
    
    for j in range(206):
        for i in range(156):#-SCALE_RIGHT):
            img_temperature[j][i] = float(downsized_og[j][i])/GRAYSCALE_CAP*(temp_range) + temp_low
    
    #cv2.imwrite("EX_out.jpg", downsized_og)
    
    #Run CV algorithms on door
    door = img_temperature[doorY1:doorY2,doorX1:doorX2] #Door pixel temperatures
    door_og = downsized_og[doorY1:doorY2,doorX1:doorX2] #Original door pixels
    door_gs = downsized_og[doorY1:doorY2,doorX1:doorX2] #Modified original door pixels
    
    kernel = np.ones((5,5),np.uint8)
    door_gs = cv2.dilate(door_gs,kernel,iterations = 1) #Dilate 
    #fig = plt.figure()
    #plt.imshow(door_gs,cmap='gray')
    
    th,_  = find_threshold(np.array(door_gs)) #Find threshold
    
    leaks = bw(door_gs,th) #Apply threshold
    kernel = np.ones((4,4))
    leaks = cv2.erode(leaks,kernel,iterations = 1) #Erode 

    #Get outline of leakage areas
    leaks = np.uint8(leaks*255)
    borders = cv2.Canny(leaks,2,4) 
    
    
    #door_ogrgb = cv2.cvtColor(door_og,cv2.COLOR_GRAY2RGB)
    
    #Plot original door on a figure then plot outline
    plt.figure()
    plt.subplot(122)
    plt.imshow(door_og,cmap='gray')
    plt.title("labeled")
    x,y = np.where(borders)[1], np.where(borders)[0]
    
    plt.axis([0,doorX2-doorX1,doorY2-doorY1,0])
    plt.scatter(x,y,color='r',marker='.')
    
    plt.subplot(121)
    plt.imshow(door_og,cmap='gray')
    plt.title("original")
    plt.savefig("final/" + im_name+".jpg")
    plt.close()
    
if __name__ == '__main__':
    doorX1,doorX2 = 50,107
    doorY1,doorY2 = 50,174
    label("EX.jpg",doorX1,doorX2,doorY1,doorY2)