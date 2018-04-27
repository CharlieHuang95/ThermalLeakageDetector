import cv2
import numpy as np
from . import helpers
import leak

#from matplotlib import pyplot as plt

def label(pa,img_path,doorX1,doorX2,doorY1,doorY2,outpath="example.jpeg",image = None):
    annotation_num = 0
    
    #Door X,Y specify bounding box of door within the original image
    
    im = cv2.imread(img_path,0)
    print("CHARLIE LOOK HERE ", im)
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

    print("door_og", door_og)
    print("y1, y2, x1, x2", doorY1, doorY2, doorX1, doorX2)
    print("door_gs", door_gs)
    
    kernel = np.ones((5,5),np.uint8)
    door_gs = helpers.dilate(door_gs,kernel,1) #Dilate 

    th,_  = helpers.find_threshold(np.array(door_gs)) #Find threshold
    
    leaks = helpers.bw(door_gs,th) #Apply threshold
    kernel = np.ones((4,4))
    leaks = helpers.erode(leaks,kernel,1) #Erode 

    #Get outline of leakage areas
    leaks = np.uint8(leaks*255)
    
    #Seaparte leakage areas into portions
    min_leak_size = int(pa.min_leak_portion * leaks.size)
    
    img_groups,num_groups,leak_classes = leak.group_leaks(leaks,min_leak_size)
    
    if len(leak_classes) > 0:
        leak.validate_leaks(leak_classes,door_gs)
    
    # if no regions are labeled
    if len(leak_classes) == 0:
        og_rgb = cv2.cvtColor(downsized_og,cv2.COLOR_GRAY2BGR)
        og_rgb = helpers.resize(og_rgb,960,1280)
        
        cv2.rectangle(og_rgb,(int(doorX1*960/156),int(doorY1*1280/206)),\
              (int(doorX2*960/156),int(doorY2*1280/206)),pa.colors[-1],thickness=2)
        cv2.putText(og_rgb,"No problems detected", (180,150),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),4)
        cv2.imwrite(outpath,og_rgb)
        return ["No error"]
    
    img_groups = (img_groups/num_groups*255).astype(int)

    og_rgb = cv2.cvtColor(downsized_og,cv2.COLOR_GRAY2BGR)
    
    conv_mask = np.zeros((206,156))
    for j in range(206):
        for i in range(156):
            conv_mask[j,i] = max(((103-j)/103)**2,((78-i)/78)**2)
    conv_mask = helpers.resize(conv_mask,door_gs.shape[1],door_gs.shape[0])
    
    #plt.imshow(img_groups,cmap='gray')
    for lk in leak_classes:
        #plt.imshow(lk.bw_img,cmap='gray')
        borders = helpers.outline_leak(lk.bw_img,2,4)
        lk.classify_leak(door_gs,conv_mask)
        
        x,y = np.where(borders)[1], np.where(borders)[0]
        og_rgb[y+doorY1,x+doorX1] = pa.colors[lk.color]
        
        annotation_num+=1
        
    #plt.imshow(og_rgb)

    og_rgb = helpers.resize(og_rgb,960,1280)

    annotation_num = 0
    detected = []

    for lk in leak_classes:
        top_ind = np.argmin([pixel[0] for pixel in lk.pixels])
        annotate_coordinates = (int(1280/206*(lk.pixels[top_ind][0]+doorY1)),int(960/156*(lk.pixels[top_ind][1]+doorX1)))
        annotate_coordinates = (180,annotation_num*50+150)
        if lk.leak_type not in detected:
            cv2.putText(og_rgb,lk.leak_type, annotate_coordinates,cv2.FONT_HERSHEY_SIMPLEX,1,pa.colors[lk.color],3)
            detected.append(lk.leak_type)
            annotation_num += 1
        
    cv2.rectangle(og_rgb,(int(doorX1*960/156),int(doorY1*1280/206)),\
                  (int(doorX2*960/156),int(doorY2*1280/206)),pa.colors[-1],thickness=2)
    
    #plt.imshow(og_rgb)    
    
    #change size here (og_rgb)
    
    cv2.imwrite(outpath,og_rgb)
    return [lk.leak_type  for lk in leak_classes]

if __name__ == '__main__':
    doorX1,doorX2 = 50,107
    doorY1,doorY2 = 50,174
    #label("EX.jpg",doorX1,doorX2,doorY1,doorY2)
