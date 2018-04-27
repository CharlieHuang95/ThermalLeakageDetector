import cv2
import numpy as np
from . import helpers
from leakage_types import LeakageTypes

#from matplotlib import pyplot as plt

def label(pa,img_path,doorX1,doorX2,doorY1,doorY2,im_name="example.jpeg",image = None):
    #Door X,Y specify bounding box of door within the original image
    
    im = cv2.imread(img_path,0)
    #plt.imshow(im,cmap='gray')
    og = np.array(im)

    ##### Denoise image###########
    im = helpers.bilateral_filter(im,9,150,150) 
    
    ##### Read temperature scales #####
    #temp_low,temp_hi = helpers.read_scale(og,pa)
    ##### Downsize image ######
    downsized_og = helpers.resize(im,156,206)
    downsized_og = helpers.denoise(downsized_og,5,7,21) #Denoise
    
    ##### Translate pixel values into temperature values #####
    #img_temperature = helpers.grayscale_to_temp(downsized_og,temp_low,temp_hi)
    
    #Run CV algorithms on door
    #door = img_temperature[doorY1:doorY2,doorX1:doorX2] #Door pixel temperatures
    door_og = downsized_og[doorY1:doorY2,doorX1:doorX2] #Original door pixels
    door_gs = downsized_og[doorY1:doorY2,doorX1:doorX2] #Modified original door pixels
    
    kernel = np.ones((5,5),np.uint8)
    door_gs = helpers.dilate(door_gs,kernel,1) #Dilate 

    th,_  = helpers.find_threshold(np.array(door_gs)) #Find threshold
    
    leaks = helpers.bw(door_gs,th) #Apply threshold
    kernel = np.ones((4,4))
    leaks = helpers.erode(leaks,kernel,1) #Erode 

    #Get outline of leakage areas
    leaks = np.uint8(leaks*255)
    borders = helpers.line_detector(leaks,2,4)
    og_rgb = cv2.cvtColor(downsized_og,cv2.COLOR_GRAY2BGR)
    
    x,y = np.where(borders)[1], np.where(borders)[0]
    og_rgb[y+doorY1,x+doorX1] = (0,0,255)
        
    conv_mask = np.zeros((206,156))
    for j in range(206):
        for i in range(156):
            conv_mask[j,i] = max(((103-j)/103)**2,((78-i)/78)**2)
    conv_mask = helpers.resize(conv_mask,door_gs.shape[1],door_gs.shape[0])
    
    
    convolution = np.sum(door_gs * helpers.bw(door_gs,th) * conv_mask)
    summ = np.sum(door_gs * helpers.bw(door_gs,th))

    # TODO: Modify this to reflect leakage type!!!
    leak_type = LeakageTypes.POOR_INSULATION_LARGE
    
    if convolution > 0.75 * summ:
        # TODO: Modify this to reflect leakage type!!!
        leak_type = LeakageTypes.AIR_LEAK_TOP
    
    top_ind = np.argmin(y)
    annotate_coordinates = (int(1280/206*(y[top_ind]+doorY1))+20,int(960/156*(x[top_ind]+doorX1)))
    og_rgb = helpers.resize(og_rgb,960,1280)

    cv2.putText(og_rgb,leak_type, annotate_coordinates,cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),3)
    cv2.imwrite(im_name,og_rgb)
    return leak_type

if __name__ == '__main__':
    doorX1,doorX2 = 50,107
    doorY1,doorY2 = 50,174
    #label("EX.jpg",doorX1,doorX2,doorY1,doorY2)