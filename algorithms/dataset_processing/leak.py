import numpy as np
#from matplotlib import pyplot as plt
import cv2
from leakage_types import LeakageTypes

class Leak():
    def __init__(self,pixels=[]):
        self.pixels = pixels
    def add_pixels(self,new_pixels):
        self.pixels.extend(new_pixels)
    def make_bw_image(self,shape):
        self.bw_img = np.zeros(shape)
        for pixel in self.pixels:
            self.bw_img[pixel] = 255
        self.bw_img = np.uint8(self.bw_img)
        
    def classify_leak(self,thermal_image,conv_mask):
        convolution = np.sum(thermal_image * self.bw_img * conv_mask)
        
        summ = np.sum(thermal_image * self.bw_img)

        if (self.is_thin() and convolution > 0.6 * summ) or convolution > 0.8 * summ:
            center_of_mass = np.zeros(2)
            total_weight = 0
            for pixel in self.pixels:
                center_of_mass += np.multiply(pixel,thermal_image[pixel])
                total_weight += thermal_image[pixel]
            center_of_mass = center_of_mass/total_weight
        
            nearest = np.argmin([center_of_mass[0],thermal_image.shape[0]-center_of_mass[0],\
            center_of_mass[1],thermal_image.shape[1]-center_of_mass[1]])
            
            if nearest == 0:
                self.leak_type = LeakageTypes.AIR_LEAK_TOP
                self.color = 0
            elif nearest == 1:    
                self.leak_type = LeakageTypes.AIR_LEAK_BOTTOM
                self.color = 1
            elif nearest ==2:
                self.leak_type = LeakageTypes.AIR_LEAK_LEFT
                self.color = 2
            elif nearest ==3:
                self.leak_type = LeakageTypes.AIR_LEAK_RIGHT
                self.color = 3
                
        else:
            if len(self.pixels) > 0.15 * self.bw_img.size:
                self.leak_type = LeakageTypes.POOR_INSULATION_LARGE
                self.color = 4
            else:
                self.leak_type = LeakageTypes.POOR_INSULATION_SMALL
                self.color = 5
                
    def is_thin(self):
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(7,7))
        eroded = cv2.erode(self.bw_img,kernel,iterations=1)
        
        if np.sum(eroded)/np.sum(self.bw_img) < 0.25:
            return True
        return False
                
    def get_avg(self,thermal_image):
        self.total = np.sum([thermal_image[pixel] for pixel in self.pixels])
        self.avg = self.total/len(self.pixels)
        
def group_leaks(all_leaks,min_size):
    n = 1
    group_numbers = np.zeros(all_leaks.shape).astype(int)
    group_to_leakage = np.zeros(all_leaks.size).astype(int)
    leakage_groups = []
    
    for i in range(all_leaks.shape[0]):
        for j in range(all_leaks.shape[1]):
            if all_leaks[i][j] < 255:
                continue
            
            if group_numbers[i][j] == 0:
                check_neighbour((i,j),(i-1,j),group_numbers,leakage_groups)
                check_neighbour((i,j),(i+1,j),group_numbers,leakage_groups)
                check_neighbour((i,j),(i,j-1),group_numbers,leakage_groups)
                check_neighbour((i,j),(i,j+1),group_numbers,leakage_groups)
                check_neighbour((i,j),(i-1,j-1),group_numbers,leakage_groups)
                check_neighbour((i,j),(i+1,j+1),group_numbers,leakage_groups)
                check_neighbour((i,j),(i+1,j-1),group_numbers,leakage_groups)
                check_neighbour((i,j),(i-1,j+1),group_numbers,leakage_groups)
                
                if group_numbers[i][j] == 0:
                    group_numbers[i][j] = n
                    leakage_groups.append([n])
                    n += 1
                
    for i in range(len(leakage_groups)):
        group = leakage_groups[i]
        for grp_num in group:
            group_to_leakage[grp_num] = i
            
    leaks = []
    
    for i in range(len(leakage_groups)):
        leaks.append(Leak(pixels=[]))
    
    display_groups = np.zeros(all_leaks.shape).astype(int)
    
    for i in range(all_leaks.shape[0]):
        for j in range(all_leaks.shape[1]):
            if all_leaks[i][j] < 255:
                continue
            leakage_number = group_to_leakage[group_numbers[i][j]]
            leaks[leakage_number].add_pixels([(i,j)])
            
    i=0
    while(i<len(leaks)):
        if len(leaks[i].pixels)<min_size:
            del leaks[i]
        else:
            i+=1
    
    for i in range(len(leaks)):
        for pixel in leaks[i].pixels:
            display_groups[pixel] = i+1
        leaks[i].make_bw_image(all_leaks.shape)
        
    return display_groups, len(leaks), leaks

def validate_leaks(leaks,thermal_image):
    
    all_sum = np.sum(thermal_image)
    leaks_sum = 0
    leaks_pixels = 0
    for leak in leaks:
        leak.get_avg(thermal_image)
        leaks_sum += leak.total
        leaks_pixels += len(leak.pixels)

    reg_sum = all_sum - leaks_sum
    reg_avg = reg_sum/(thermal_image.size-leaks_pixels)

    i=0
    while(i<len(leaks)):
        if (leaks[i].avg - reg_avg) < 25:
            del leaks[i]
        else:
            i+=1
    
def check_neighbour(point, neighbour,group_numbers,leakage_groups):
    if neighbour[0] < 0 or neighbour[0] >= group_numbers.shape[0]:
        return
    if neighbour[1] < 0 or neighbour[1] >= group_numbers.shape[1]:
        return
    
    if group_numbers[neighbour]==0 or group_numbers[neighbour] == group_numbers[point]:
        return
    
    if group_numbers[point] == 0:
        group_numbers[point] = group_numbers[neighbour]
        return
    
    #point is in a group already and different from neighbour, update leakage groups
    lk_grp_n,lk_grp_p = -1,-1
    for i in range(len(leakage_groups)):
        if group_numbers[point] in leakage_groups[i]:
            lk_grp_p = i
        if group_numbers[neighbour] in leakage_groups[i]:
            lk_grp_n = i
    
    assert(lk_grp_n > -1)
    assert(lk_grp_p > -1)
    
    if lk_grp_p != lk_grp_n:
        mi = min(lk_grp_p,lk_grp_n)
        ma = max(lk_grp_p,lk_grp_n)
        leakage_groups[mi] += leakage_groups[ma]
        del leakage_groups[ma]

if __name__ == '__main__':
    test = np.zeros((100,100))
    
    for i in range(100):
        for j in range(100):
            test[i][j] = int((i**2+j**2) < 64**2) * 255
    
    test = cv2.imread('test.jpg',0)
    for i in range(test.shape[0]):
        for j in range(test.shape[1]):
            if test[i][j] > 130:
                test[i][j] = 255
            else:
                test[i][j] = 0
    
    #plt.imshow(test,cmap='gray')
    
    d,num_groups,leaks = group_leaks(test,700)
    d = (d/num_groups*255).astype(int)
    
    #plt.imshow(d,cmap='gray')
    
    
    
    
    
    
