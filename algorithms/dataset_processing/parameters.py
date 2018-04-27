import numpy as np

class Parameters:
    def __init__(self):
        self.SCALE_LEFT = 34
        self.SCALE_RIGHT = 127
        self.HIGH_BOT = 32
        self.LOW_TOP = 1249
        self.numbers = '-0123456789'
        
        self.WIDTH = 960
        self.HEIGHT = 1280
        
        self.min_leak_portion = 0.03
        
        self.colors = [(0,0,255),(0,255,0),(255,0,0),(255,255,0),(0,255,255),(255,0,255),(255,255,255)]