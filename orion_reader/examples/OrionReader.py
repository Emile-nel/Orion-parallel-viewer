## Needed Imports
from PCANBasic import *
import string  
import time
import threading
import os
from PCANOrionReader import *
from OrionView import *


IS_WINDOWS = platform.system() == 'Windows'


#run if this is the main script being run
if __name__ == '__main__':
    if IS_WINDOWS:
        ## Starts the program
        TimerRead()
        #Run windows with PCAN device reader
    else:
        #Run Raspberry pi setup with socketCAN
        print("gogo raspberry")
    
