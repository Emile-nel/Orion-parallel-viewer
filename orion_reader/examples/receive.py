
import os
from enum import Enum
#from pyexpat.errors import messages
#from tkinter import Listbox
#from xml.dom.expatbuilder import FragmentBuilder
import can
import threading
import sys
import curses
import traceback

from tkinter import *
ws = Tk()
ws.title('Orion Reader')
ws.geometry('960x544')




stop_bus = threading.Event()

thread_exception = None

can_messages = {}


WHITELIST_IDs = []#[0x3b1,0x3b2,0x3b3] #List of message IDs that we want. 


id_list = [0x3b1,0x3b2,0x3b3]
id_read =[]
msg_list = []

class BitOrder(Enum):
    LSB = 0
    MSB = 1

class ByteOrder(Enum):
    LittleEndian = 0
    BigEndian = 1

class CANMessage:
    def __init__(self, name, id,startByte,len=8,bitOrder=BitOrder.MSB,byteOrder=ByteOrder.BigEndian,factor=1):
        self.name       = name      #Message name as a string   
        self.id         = id        #Message ID
        self.startByte  = startByte #Message startbyte in message
        self.len        = len       #Length of message in bits(default = 8)
        self.bitOrder   = bitOrder  #bit order of Byte, either 0 = LSB or 1 = MSB(default)
        self.byteOrder  = byteOrder #byte order of message, either 0 = LittleEndian, 1 = BigEndian(default)
        self.factor     = factor    #Multiplication factor of message


      
#Message list coming from the Master BMS
CANMsgs_Master = [
    #0x3b1
CANMessage('Pack_Current',0x3b1,0,16,BitOrder.MSB,ByteOrder.BigEndian,0.1),
CANMessage('Inst_Voltage',0x3b1,16,16,BitOrder.MSB,ByteOrder.BigEndian,0.1),
CANMessage('Pack_SOC',0x3b1,32,8,BitOrder.MSB,ByteOrder.BigEndian,0.5),
CANMessage('Relay_State',0x3b1,40,8,BitOrder.MSB,ByteOrder.BigEndian,1),
    #0x3b2
CANMessage('Pack_DCL',0x3b2,0,16,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('Pack_CCL',0x3b2,16,8,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('High_Temperature',0x3b2,32,8,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('Low_Temperature',0x3b2,40,8,BitOrder.MSB,ByteOrder.BigEndian,1),
    #0x3b3 - unit error messages
CANMessage('',0x3b3,0,1,BitOrder.MSB,ByteOrder.BigEndian,1), 
CANMessage('',0x3b3,1,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('',0x3b3,2,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('',0x3b3,3,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('',0x3b3,4,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('',0x3b3,5,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('',0x3b3,6,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('',0x3b3,7,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('',0x3b3,8,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('',0x3b3,9,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('',0x3b3,10,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('',0x3b3,11,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('',0x3b3,12,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('',0x3b3,13,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('',0x3b3,14,1,BitOrder.MSB,ByteOrder.BigEndian,1),  
CANMessage('',0x3b3,15,1,BitOrder.MSB,ByteOrder.BigEndian,1), 
CANMessage('',0x3b3,16,1,BitOrder.MSB,ByteOrder.BigEndian,1), 
CANMessage('',0x3b3,17,1,BitOrder.MSB,ByteOrder.BigEndian,1), 
CANMessage('',0x3b3,18,1,BitOrder.MSB,ByteOrder.BigEndian,1), 
CANMessage('',0x3b3,19,1,BitOrder.MSB,ByteOrder.BigEndian,1), 
CANMessage('',0x3b3,20,1,BitOrder.MSB,ByteOrder.BigEndian,1), 
CANMessage('',0x3b3,21,1,BitOrder.MSB,ByteOrder.BigEndian,1), 
CANMessage('',0x3b3,22,1,BitOrder.MSB,ByteOrder.BigEndian,1), 
CANMessage('',0x3b3,23,1,BitOrder.MSB,ByteOrder.BigEndian,1), 
CANMessage('',0x3b3,24,1,BitOrder.MSB,ByteOrder.BigEndian,1), 
CANMessage('',0x3b3,25,1,BitOrder.MSB,ByteOrder.BigEndian,1), 

    #0x3b3 - Parallel string specific error messages
CANMessage('',0x3b3,30,1,BitOrder.MSB,ByteOrder.BigEndian,1), 
CANMessage('',0x3b3,31,1,BitOrder.MSB,ByteOrder.BigEndian,1), 
]
#Message list coming from the Slave1 BMS
CANMsgs_Slave1 = []
#Message list coming from the Slave2 BMS
CANMsgs_Slave2 = []
#Message list coming from the Slave3 BMS
CANMsgs_Slave3 = []


def read_bus(bus_device):
    #Read data from 'bus_device' until the nect newline character
    message = bus.recv(0.2)
    while True:
        if message:
            break
        message = bus.recv(0.2)

    try:
        messageString =  "{}:ID={}:LEN={}".format("RX", message.arbitration_id, message.dlc)
        for x in range(message.dlc):
            messageString += ":{:02x}".format(message.data[x])        
    #print exception if failed to parse the CAN message into the string.
    except Exception as e:
        print(e)
    return(messageString)


def bus_run_loop(bus_device):
    #Background thread ofr serial reading
    try:
        while not stop_bus.is_set():
            messageString = read_bus(bus_device)
            #Sample Frame: FRAME:ID=246:LEN=8:8E:62:1C:F6:1E:63:63:20
            # Split it into an array (e.g. ['FRAME', 'ID=246', 'LEN=8', '8E', '62', '1C', 'F6', '1E', '63', '63', '20'])
            frame =  messageString.split(':')

            try: 
                frame_id = int(frame[1][3:]) # get the ID from the 'ID=246' string
                #Check if can ID is in whitelist and do some stuff with it if it is. Else, leave it alone

                if frame_id in WHITELIST_IDs:
                    print('CAN ID in whitelist. I will do some stuff later on.')
                    continue
            except:
                print('Something clearly went wrong here bry')
            print(messageString)

    except:
        print('the bus stopped.. Why did the bus stop? !!')


def populate_whitelist():
    for messages in [CANMsgs_Master,CANMsgs_Slave1,CANMsgs_Slave2,CANMsgs_Slave3]:
        if messages.id not in WHITELIST_IDs:
            WHITELIST_IDs.append(messages.id)
    print(WHITELIST_IDs)
    

#run if this is the main script being run
if __name__ == '__main__':
    try: 
        os.system('sudo ip link set can0 type can bitrate 500000')
        os.system('sudo ifconfig can0 up')
        bus = can.interface.Bus(channel = 'can0', bustype = 'socketcan')# socketcan_native
        #populate the whitelist ID list
        populate_whitelist()
        # Start the bus reading in the background thread
        bus_thread = threading.Thread(target=bus_run_loop, args=(bus,))
        bus_thread.start()

        # Start the main loop
        ws.mainloop()
      

    except:
        print('Sorry, the bus could not be started')
    finally:
        if bus_thread:

            stop_bus.set()
            bus_thread.join()

            #end the socketCan session
            os.system('sudo ifconfig can0 down')

            #print the exception if the thread returned one
            if thread_exception:
                traceback.print_exception(*thread_exception)
                sys.stderr.flush()
            else:
                print('The bus is being stopped safely')



