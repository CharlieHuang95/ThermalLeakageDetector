import usb.core
import usb.util
import sys
from PIL import Image, ImageTk
import numpy
from numpy import array
import colorscale
from scipy.misc import toimage
from scipy import ndimage
 
 
class PhotoTaker():
 
    def __init__(self):
        self.palettes = dict()
        self.palettes['tillscale'] = colorscale.TillPalette()
        self.palettes['gray1scale'] = colorscale.Gray1Palette()
        self.palettes['redgreenscale'] = colorscale.RedGreenPalette()
        self.palettes['greenredscale'] = colorscale.GreenRedPalette()
        self.palettes['rain1scale'] = colorscale.Rain1Palette()
        self.palettes['ironscale'] = colorscale.IronPalette()
        self.palettes['blackhotscale'] = colorscale.BlackHotPalette()
        self.palettes['whitehotscale'] = colorscale.WhiteHotPalette()
        self.status = None
        self.calImage = None
        self.calImagex = None
        self.dev = None
        self.label = None
        self.Label1 = None
        self.Label2 = None
        self.Label3 = None
        self.Label4 = None
        self.Label5 = None
        self.Label6 = None
        self.scl = None
        self.scl1 = None
        self.scl2 = None
        self.calImage = None
        self.calImagex = None
        self.pal = None
        self.snapshot = None
        self.initialize()
 
    def initialize(self):
        # Default palette is "iron"
        # global dev, label, Label1, Label2, Label3, Label4, Label5, Label6
        # global scl, scl1, scl2
        # global calImage, calImagex, pal, snapshot
        self.pal = 'gray1scale'
        self.snapshot = 0
 
        # Set up device
        self.dev = self.usbinit()
        self.camerainit(self.dev)
 
        # get a cal image so the data isn't null if/when we miss the first one
        self.get_cal_image(self.dev)
 
 
    def deinit(self,dev):
        msg = '\x00\x00'
        for i in range(3):
            self.send_msg(dev,0x41, 0x3C, 0, 0, msg)           # 0x3c = 60  Set Operation Mode 0x0000 (Sleep)
 
    def usbinit(self):
        # find our Seek Thermal device  289d:0010
        dev = usb.core.find(idVendor=0x289d, idProduct=0x0010)
 
        # was it found?
        if dev is None:
            raise ValueError('Device not found')
 
        # set the active configuration. With no arguments, the first
        # configuration will be the active one
        dev.set_configuration()
 
        # get an endpoint instance
        cfg = dev.get_active_configuration()
        intf = cfg[(0,0)]
 
        # match the first OUT endpoint
        ep = usb.util.find_descriptor(
            intf,
            custom_match = \
            lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == \
                usb.util.ENDPOINT_OUT)
 
        assert ep is not None
 
        return dev
 
 
    # send_msg sends a message that does not need or get an answer
    def send_msg(self,dev,bmRequestType, bRequest, wValue=0, wIndex=0, data_or_wLength=None, timeout=None):
        assert (dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data_or_wLength, timeout) == len(data_or_wLength))
 
 
    # receive msg actually sends a message as well.
    def receive_msg(self,dev,bmRequestType, bRequest, wValue=0, wIndex=0, data_or_wLength=None, timeout=None):
        zz = dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data_or_wLength, timeout) # == len(data_or_wLength))
        return zz
 
    def camerainit(self, dev):
        try:
            msg = '\x01'
            self.send_msg(dev,0x41, 0x54, 0, 0, msg)                 # 0x54 = 84 Target Platform 0x01 = Android
        except Exception as e:
            self.deinit(dev)
            msg = '\x01'
            self.send_msg(dev,0x41, 0x54, 0, 0, msg)                 # 0x54 = 84 Target Platform 0x01 = Android
 
        self.send_msg(dev,0x41, 0x3C, 0, 0, '\x00\x00')              # 0x3c = 60 Set operation mode    0x0000  (Sleep)
        ret1 = self.receive_msg(dev,0xC1, 0x4E, 0, 0, 4)             # 0x4E = 78 Get Firmware Info
 
        ret2 = self.receive_msg(dev,0xC1, 0x36, 0, 0, 12)            # 0x36 = 54 Read Chip ID
 
        self.send_msg(dev,0x41, 0x56, 0, 0, '\x20\x00\x30\x00\x00\x00')                  # 0x56 = 86 Set Factory Settings Features
        ret3 = self.receive_msg(dev,0xC1, 0x58, 0, 0, 0x40)                              # 0x58 = 88 Get Factory Settings
 
        self.send_msg(dev,0x41, 0x56, 0, 0, '\x20\x00\x50\x00\x00\x00')                  # 0x56 = 86 Set Factory Settings Features
        ret4 = self.receive_msg(dev,0xC1, 0x58, 0, 0, 0x40)                              # 0x58 = 88 Get Factory Settings
 
        self.send_msg(dev,0x41, 0x56, 0, 0, '\x0C\x00\x70\x00\x00\x00')                  # 0x56 = 86 Set Factory Settings Features
        ret5 = self.receive_msg(dev,0xC1, 0x58, 0, 0, 0x18)                              # 0x58 = 88 Get Factory Settings
 
        self.send_msg(dev,0x41, 0x56, 0, 0, '\x06\x00\x08\x00\x00\x00')                  # 0x56 = 86 Set Factory Settings Features  
        ret6 = self.receive_msg(dev,0xC1, 0x58, 0, 0, 0x0C)                              # 0x58 = 88 Get Factory Settings
 
        self.send_msg(dev,0x41, 0x3E, 0, 0, '\x08\x00')                                  # 0x3E = 62 Set Image Processing Mode 0x0008
        ret7 = self.receive_msg(dev,0xC1, 0x3D, 0, 0, 2)                                 # 0x3D = 61 Get Operation Mode
 
        self.send_msg(dev,0x41, 0x3E, 0, 0, '\x08\x00')                                  # 0x3E = 62 Set Image Processing Mode  0x0008
        self.send_msg(dev,0x41, 0x3C, 0, 0, '\x01\x00')                                  # 0x3c = 60 Set Operation Mode         0x0001  (Run)
        ret8 = self.receive_msg(dev,0xC1, 0x3D, 0, 0, 2)                                 # 0x3D = 61 Get Operation Mode
 
 
    def read_frame(self,dev):
        # Send a read frame request
        # 0x53 = 83 Set Start Get Image Transfer
        self.send_msg(dev,0x41, 0x53, 0, 0, '\xC0\x7E\x00\x00')
        try:
            data  = dev.read(0x81, 0x3F60, 1000)
            data += dev.read(0x81, 0x3F60, 1000)
            data += dev.read(0x81, 0x3F60, 1000)
            data += dev.read(0x81, 0x3F60, 1000)
 
        except usb.USBError as e:
            sys.exit()
 
        return data
 
 
    # Add (really subtract) the data from the 207 row to each pixil
    def add_207(self,imgF):
        # global scl2
        # or not depending on the testing some of the following may be commented out.
        # there are a different # of black dots in each row so the divisor
        # needs to change for each row according to what is in the dot_numbers.txt file.
        # this may not be the best way to do this. The code below does not do this now.
        # need to try to use numpy or scipy to do this as it is a real hit on cpu useage.
        # But doing it only for the cal image doesn't impact the real time images.
        tuning = self.scl2.get() / 150.0
 
        z = (.002 * imgF[:,206].mean())
        z1 = z * tuning
 
        for i in range(0,156,1):
            for j in range(0,205,1):
                    # try scaled pixil and scaled pixil 207
                    imgF[i,j] = imgF[i,j] - (.05 * imgF[i,j]/z) - imgF[i,206]/z1
 
        return
 
 
    def get_cal_image(self, dev):
        # Get the first cal image so calImage isn't null
        # global status, calImage, calImagex
        self.status = 0
 
        #  Wait for the cal frame
        while self.status != 1:
            #  1 is a Calibration frame
            # Read a raw frame
            ret9 = self.read_frame(dev)
            self.status = ret9[20]
            status1 = ret9[80]
            #  6 is a pre-calibration frame (whatever that means)
            #  4, 9, 8, 7, 5, 10 other... who knows.
            #  See http://www.eevblog.com/forum/testgear/yet-another-cheap-thermal-imager-incoming/msg545910/#msg545910
            #  for examples.
 
        #  Convert the raw 16 bit calibration data to a PIL Image
        calimgI = Image.frombytes("F", (208,156), ret9, "raw", "F;16")
 
        # save 16bit cal image for later
        self.calImagex = Image.frombytes("I", (208,156), ret9, "raw", "I;16")
 
        #  Convert the PIL Image to an unsigned numpy float asarray
        im2arr = numpy.asarray(calimgI)
 
        # clamp values < 2000 to 2000
        im2arr = numpy.where(im2arr < 2000, 2000, im2arr)
        im2arrF = im2arr.astype('float')
        self.calImage = im2arrF
 
        return
 
 
    def get_image(self):
        dev = self.dev
        # global calImage, calImagex, status, scl, scl1, pal, snapshot
        self.status = 0
 
        #  Wait for the next image frame, ID = 3 is a Normal frame
        while self.status != 3:
            # Read a raw frame
           ret9 = self.read_frame(dev)
           self.status = ret9[20]
 
            # check for a new cal frame, if so update the cal image
           if self.status == 1:
                # Convert the raw 16 bit calibration data to a PIL Image
                calimgI = Image.frombytes("F", (208,156), ret9, "raw", "F;16")
                # save cal 16bit image for later
                self.calImagex = Image.frombytes("I", (208,156), ret9, "raw", "I;16")
                # Convert the PIL Image to an unsigned numpy float array
                im2arr = numpy.asarray(calimgI)
                # Pixel 40 is a counter of some sort that starts at 0 and increments to 65535
                # maybe an internal frame counter or clock.
                status1 = im2arr[0,40]
                # clamp values < 2000 to 2000
                im2arr = numpy.where(im2arr < 2000, 2000, im2arr)
                im2arrF = im2arr.astype('float')
                # Clamp pixel 40 to 2000 so it doesn't cause havoc as it rises to 65535
                im2arrF[0,40] = 2000
                # Add the row 207 correction (maybe) >>Looks like it needs to be applied to just the cal frame<<
                # self.add_207(im2arrF)
                # Zero out column 207
                im2arrF[:,206] = numpy.zeros(156)
                #  Print the min max values for the calimage (Some Tinker related stuff)
                #  self.printCAL(im2arrF)
                #  Save the calibration image
                self.calImage = im2arrF
 
        #  If this is normal image data
        #  Convert the raw 16 bit thermal data to a PIL Image
        imgx = Image.frombytes("F", (208,156), ret9, "raw", "F;16")
        imgy = Image.frombytes("I", (208,156), ret9, "raw", "I;16")
 
        #  Convert the PIL Image to an unsigned numpy float array
        im1arr = numpy.asarray(imgx)
 
        # clamp values < 2000 to 2000
        im1arr = numpy.where(im1arr < 2000, 2000, im1arr)
        im1arrF = im1arr.astype('float')
 
        # Clamp pixel 40 to 2000 so it doesn't cause havoc as it rises to 65535
        im1arrF[0,40]  = 2000
 
        # Zero out column 207
        im1arrF[:,206] = numpy.zeros(156)
 
        #  Print the min max values for the image (UI related stuff)
        #  self.printIMG(im1arrF)
 
        #  Subtract the most recent calibration image from the offset image data
        #  With both the cal and image as floats, the offset doesn't matter and
        #  the following image conversion scales the result to display properly
        additionF = (im1arrF) + 600 - (self.calImage)
 
        #  Try removing noise from the image, this works suprisingly well, but takes some cpu time
        #  It gets rid of bad pixels as well as the "Patent Pixils"
        noiselessF = ndimage.median_filter(additionF, 3)
 
        # don't bother to zero out column 207 as it contains no data
        # can't see any difference on the image anyway.
        # noiselessF[:,206] = numpy.zeros(156)
 
        #  Print the min max values for the calibrated/noise filtered image (UI related stuff)
        #  self.printSUM(noiselessF)
 
        # This will colorize the image, it works but it is a cpu hog
        #bottom = self.scl.get()
        #top = self.scl1.get()
        #display_min = bottom * 4
        #display_max = top * 16
        image8 = noiselessF
        #image8.clip(display_min, display_max, out=image8)
        #image8 -= display_min
        #image8 //= (display_max - display_min + 1) / 256.
        image8 = image8.astype(numpy.uint8)
        noiselessI8= image8
        conv = colorscale.GrayToRGB(self.palettes[self.pal])
        cred = numpy.frompyfunc(conv.get_red, 1, 1)
        cgreen = numpy.frompyfunc(conv.get_green, 1, 1)
        cblue = numpy.frompyfunc(conv.get_blue, 1, 1)
 
        # Convert to a PIL image sized to 640 x 480
        color = numpy.dstack((cred(noiselessI8).astype(noiselessI8.dtype), cgreen(noiselessI8).astype(noiselessI8.dtype), cblue(noiselessI8).astype(noiselessI8.dtype)))
        imgCC = Image.fromarray(color).resize((640, 480),Image.ANTIALIAS).transpose(3)
 
        # If user has clicked Snap! then save the rawCal, rawData, and colorized image
        # File names are hardcoded for now.

        im1arry = numpy.asarray(imgy)
        im1arrz = numpy.asarray(self.calImagex)
        jj = Image.fromarray(im1arry)
        jj.save('data/rawData.png')
        jj = Image.fromarray(im1arrz)
        jj.save('data/rawCal.png')
        imgCC.save('data/CImage.png')

        return imgCC
 
if __name__ == "__main__":
    pt = PhotoTaker()
    pt.get_image()