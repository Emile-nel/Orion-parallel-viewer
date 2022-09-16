
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
from datetime import datetime

import tkinter as tk

ws = tk.Tk()





stop_bus = threading.Event()

thread_exception = None

can_messages    = {}
cell_info       = []
for i in range(1,45,1):
    cell_info.append({'Broadcast_Cell_ID':i,'Broadcast_Cell_Intant_Voltage': 0.0, 'Broadcast_Cell_Resistance': 0.0,'Broadcast_Cell_Open_Voltage' : 0.0})






WHITELIST_IDs = []#[0x3b1,0x3b2,0x3b3] #List of message IDs that we want. 


id_list = [0x3b1,0x3b2,0x3b3]
id_read =[]
msg_list = []

class BitOrder(Enum):
    LSB = 0
    MSB = 1

class ByteOrder(Enum):
    LittleEndian = "little"
    BigEndian = "big"

class CANMessage:


    
    def __init__(self, name, id,startBit,len=8,bitOrder=BitOrder.MSB,byteOrder=ByteOrder.BigEndian,factor=1,value=None, timeStamp =None):
        self.name       = name      #Message name as a string   
        self.id         = id        #Message ID
        self.startBit  = startBit   #Message startBit in message
        self.len        = len       #Length of message in bits(default = 8)
        self.bitOrder   = bitOrder  #bit order of Byte, either 0 = LSB or 1 = MSB(default)
        self.byteOrder  = byteOrder #byte order of message, either 0 = LittleEndian, 1 = BigEndian(default)
        self.factor     = factor    #Multiplication factor of message
        self.value      = value     
        self.timeStamp  = timeStamp

    def set_val(self,data,messageTime):
        #get the byte position of the message [0 --> 7]
        bytePos = int(self.startBit / 8)


        try:
            if self.len == 1:
                bitPos = self.startBit - 8*bytePos
                bitState = bool(int(data[bytePos])&(1<<bitPos))
                self.value = bitState
                
                

                # if bitState:
                    
                    # print('id : ' + str(self.id))
                    # print('Byte Position : ' + str(bytePos))
                    # print('byte Value : ' + str(data[bytePos]))
                
                    # print(data)
                    # print('Bit Position : ' + str(bitPos))
                    # print(str(bitState) + ' ' + (self.name))



            else:
                # get the number of bytes for the message
                byteNum = int(self.len / 8)
                if byteNum == 1:
                    self.value = data[bytePos]*self.factor
                else:
                    valueInts = data[bytePos:byteNum+bytePos]
                    ValueBytes = bytes(valueInts)
                    if self.byteOrder == ByteOrder.BigEndian:
                        self.value = int.from_bytes(ValueBytes,"big")*self.factor
                    else:
                        self.value = int.from_bytes(ValueBytes,"little")*self.factor

                # if self.id == 0x3b1:
                #     print('id : ' + str(self.id))
                #     print('Byte Position : ' + str(bytePos))
                #     print((data))
                #     print('Value : ' + str(self.value))

   
            
            #if the above succeeds... 
            self.timeStamp = messageTime
            return self.value
        except:
            print('There was an error')


      
#Message list coming from the Master BMS
CANMsgs_Master = [
# CANMessage('Broadcast_Cell_ID',             0xe3,0,8,BitOrder.MSB,ByteOrder.BigEndian,1),  
# CANMessage('Broadcast_Cell_Intant_Voltage', 0xe3,8,16,BitOrder.MSB,ByteOrder.BigEndian,0.1),    #Units in mV
# CANMessage('Broadcast_Cell_Resistance',     0xe3,24,16,BitOrder.MSB,ByteOrder.BigEndian,0.01),  #Units in mOhm 
# CANMessage('Broadcast_Cell_Open_Voltage',   0xe3,40,16,BitOrder.MSB,ByteOrder.BigEndian,0.1),   #Units in mV
    #0x3b1
CANMessage('Master_Pack_Current',      0x3b1,0,16,BitOrder.MSB,ByteOrder.BigEndian,0.1),
CANMessage('Master_Inst_Voltage',      0x3b1,16,16,BitOrder.MSB,ByteOrder.BigEndian,0.1),
CANMessage('Master_Pack_SOC',          0x3b1,32,8,BitOrder.MSB,ByteOrder.BigEndian,0.5),
CANMessage('Master_Relay_State',       0x3b1,40,8,BitOrder.MSB,ByteOrder.BigEndian,1),
    #0x3b2
CANMessage('Master_Pack_DCL',          0x3b2,0,16,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('Master_Pack_CCL',          0x3b2,16,8,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('Master_High_Temperature',  0x3b2,32,8,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('Master_Low_Temperature',   0x3b2,40,8,BitOrder.MSB,ByteOrder.BigEndian,1),
    #0x3b3 - unit error messages
CANMessage('DTC P0A1F : Internal Cell Communication',   0x3b3,0,1,BitOrder.MSB,ByteOrder.BigEndian,1), 
CANMessage('DTC P0A12 : Cell Balancing Stuck Off',      0x3b3,1,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('DTC P0A80 : Weak Cell',                     0x3b3,2,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('DTC P0AFA : Low Cell Voltage',              0x3b3,3,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('DTC P0A04 : Cell Open Wiring',              0x3b3,4,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('DTC P0AC0 : Current Sensor',                0x3b3,5,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('DTC P0A0D : Cell Voltage Over 5V',          0x3b3,6,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('DTC P0A0F : Cell Bank',                     0x3b3,7,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('DTC P0A02 : Weak Pack',                     0x3b3,8,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('DTC P0A81 : Fan Monitor',                   0x3b3,9,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('DTC P0A9C : Thermistor',                    0x3b3,10,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('DTC U0100 : CAN Communication',             0x3b3,11,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('DTC P0560 : Redundant Power Supply',        0x3b3,12,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('DTC P0AA6 : High Voltage Isolation',        0x3b3,13,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('DTC P0A05 : Invalid Input Supply Voltage',  0x3b3,14,1,BitOrder.MSB,ByteOrder.BigEndian,1),  
CANMessage('DTC P0A06 : ChargeEnable Relay',            0x3b3,15,1,BitOrder.MSB,ByteOrder.BigEndian,1), 
CANMessage('DTC P0A07 : DischargeEnable Relay',         0x3b3,16,1,BitOrder.MSB,ByteOrder.BigEndian,1), 
CANMessage('DTC P0A08 : Charger Safety Relay',          0x3b3,17,1,BitOrder.MSB,ByteOrder.BigEndian,1), 
CANMessage('DTC P0A09 : Internal Hardware',             0x3b3,18,1,BitOrder.MSB,ByteOrder.BigEndian,1), 
CANMessage('DTC P0A0A : Internal Heatsink Thermistor',  0x3b3,19,1,BitOrder.MSB,ByteOrder.BigEndian,1), 
CANMessage('DTC P0A0B : Internal Logic',                0x3b3,20,1,BitOrder.MSB,ByteOrder.BigEndian,1), 
CANMessage('DTC P0A0C : Highest Cell Voltage Too High', 0x3b3,21,1,BitOrder.MSB,ByteOrder.BigEndian,1), 
CANMessage('DTC P0A0E : Lowest Cell Voltage Too Low',   0x3b3,22,1,BitOrder.MSB,ByteOrder.BigEndian,1), 
CANMessage('DTC P0A10 : Pack Too Hot',                  0x3b3,23,1,BitOrder.MSB,ByteOrder.BigEndian,1), 
CANMessage('Balancing_Active',                          0x3b3,24,1,BitOrder.MSB,ByteOrder.BigEndian,1), 
CANMessage('MultiPurpose_Enable',                       0x3b3,25,1,BitOrder.MSB,ByteOrder.BigEndian,1), 
CANMessage('Charge Enable Inverted',                    0x3b3,26,1,BitOrder.MSB,ByteOrder.BigEndian,1),
    #0x3b3 - Parallel string specific error messages
CANMessage('Parallel Combined Charge Enable Inverted',0x3b3,30,1,BitOrder.MSB,ByteOrder.BigEndian,1), 
CANMessage('Parallel Combined Faults Present',0x3b3,31,1,BitOrder.MSB,ByteOrder.BigEndian,1), 

CANMessage('Parallel Combined Faults Present',227,31,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('Parallel Combined Faults Present',853,31,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('Parallel Combined Faults Present',849,31,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('Parallel Combined Faults Present',858,31,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('Parallel Combined Faults Present',854,31,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('Parallel Combined Faults Present',852,31,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('Parallel Combined Faults Present',896,31,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('Parallel Combined Faults Present',882,31,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('Parallel Combined Faults Present',883,31,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('Parallel Combined Faults Present',897,31,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('Parallel Combined Faults Present',884,31,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('Parallel Combined Faults Present',886,31,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('Parallel Combined Faults Present',887,31,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('Parallel Combined Faults Present',889,31,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('Parallel Combined Faults Present',885,31,1,BitOrder.MSB,ByteOrder.BigEndian,1),
CANMessage('Parallel Combined Faults Present',4,31,1,BitOrder.MSB,ByteOrder.BigEndian,1),
]


def clear_fault_codes(unitId):
    #use unitId of 0x7df to clear DTC faults on all units

    # OBDII Message structure arbitration_id=PID_REQUEST,data=[0x02 [ message length],0x01 [service code],Parameter PID,0x00,0x00,0x00,0x00,0x00],extended_id=False

   

    msg = can.Message(arbitration_id=unitId, data=[0x01, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], is_extended_id=False)
    # msg = can.Message(arbitration_id=0x7e3, data=[0x02, 0x04, 0xf0, 0x04, 0x00, 0x00, 0x00, 0x00], is_extended_id=False)
    bus.send(msg)
    print('Device with OBDII ID, '+hex(unitId) + ', fault codes cleared ')

def read_bus(bus_device):
    #Read data from 'bus_device' until the nect newline character
    message = bus.recv(0.2)
    while True:
        if message:
            break
        message = bus.recv(0.2)
        

    try:
        # if message.arbitration_id == 947:    
        #     print(list(message.data))

        messageData = list(message.data)
        messageString =  "{}:ID={}:LEN={}".format("RX", message.arbitration_id, message.dlc)
        for x in range(message.dlc):
            messageString += ":{:02x}".format(message.data[x])        
    #print exception if failed to parse the CAN message into the string.
    except Exception as e:
        print(e)
    
    date_time = datetime.fromtimestamp(message.timestamp)
    #print(date_time)
    return(message.arbitration_id,message.dlc,messageData,message.timestamp)


def bus_run_loop(bus_device):
    #Background thread ofr serial reading
    try:
        while not stop_bus.is_set():
            messageId,messageLen,messageData,messageTime = read_bus(bus_device)
            # print(messageString)
            #Sample Frame: FRAME:ID=246:LEN=8:8E:62:1C:F6:1E:63:63:20
            # Split it into an array (e.g. ['FRAME', 'ID=246', 'LEN=8', '8E', '62', '1C', 'F6', '1E', '63', '63', '20'])
            # frame =  messageString.split(':')

            try: 
                # frame_id = int(frame[1][3:]) # get the ID from the 'ID=246' string
                #Check if can ID is in whitelist and do some stuff with it if it is. Else, leave it alone

                if messageId == 0xe3:
                    cellId          = messageData[0]
                    #Extract instant voltage in mV
                    valueInts = messageData[1:3]
                    ValueBytes = bytes(valueInts)
                    cellInstVoltage = int.from_bytes(ValueBytes,"big")*0.1
                    #Extract Cell resistance in mOhm
                    valueInts = messageData[3:5]
                    ValueBytes = bytes(valueInts)
                    cellResistance = int.from_bytes(ValueBytes,"big")*0.01
                    #Extract Cell Open Voltage in mV
                    valueInts = messageData[5:7]
                    ValueBytes = bytes(valueInts)
                    cellOpenVoltage = int.from_bytes(ValueBytes,"big")*0.1
                    #update cell info list

                    cell_info[cellId - 1]['Broadcast_Cell_ID'] = cellId
                    cell_info[cellId - 1]['Broadcast_Cell_Intant_Voltage'] = cellInstVoltage
                    cell_info[cellId - 1]['Broadcast_Cell_Resistance'] = cellResistance
                    cell_info[cellId - 1]['Broadcast_Cell_Open_Voltage'] = cellOpenVoltage                        
                      
                if messageId in WHITELIST_IDs:
                    #convert the hex strings array to an integer array
                    # data = [byte for byte in frame[3:]]
                    # data = [int(byte, 16) for byte in frame[3:]]
                    #Sanity check
                    #data = [byte for byte in data if byte >= 0 and byte <= 255] 
                    # print(data)
                    

                    for message in CANMsgs_Master:
                        
                        if messageId == message.id:
                            message.set_val(messageData,messageTime)





                    #Iterate aga ---- Come back to at a later stage 
                    # for message in CANMsgs_Master:
                    #     while message.id == 0xe3:
                    #         if message.value == None: #Break the for loop because no cell values have been read yet
                    #             break
                    #         #print(message.value)
                    #         if message.name == 'Broadcast_Cell_ID':
                    #             self.cellId          = message.value
                    #             print(cellId)
                    #         if message.name == 'Broadcast_Cell_Intant_Voltage':
                    #             cellInstVoltage = message.value
                    #             print(cellInstVoltage)
                    #         if message.name == 'Broadcast_Cell_Resistance':
                    #             cellResistance  = message.value
                    #             print(cellResistance)
                    #         if message.name == 'Broadcast_Cell_Open_Voltage':
                    #             cellOpenVoltage = message.value
                    #             print(cellOpenVoltage)
                    #         #if cellId & cellInstVoltage & cellResistance & cellOpenVoltage:
                    #         if len(cell_info) < cellId: #Append the list if the current cell info has not been added yet
                    #             cell_info.append({'Broadcast_Cell_ID':cellId,'Broadcast_Cell_Intant_Voltage': cellInstVoltage, 'Broadcast_Cell_Resistance': cellResistance,'Broadcast_Cell_Open_Voltage' : cellOpenVoltage})
                    #         elif len(cell_info) == cellId: #Modify the list if the current cell in the list is being read,. 
                    #             cell_info[cellId - 1]['Broadcast_Cell_ID'] = cellId
                    #             cell_info[cellId - 1]['Broadcast_Cell_Intant_Voltage'] = cellInstVoltage
                    #             cell_info[cellId - 1]['Broadcast_Cell_Resistance'] = cellResistance
                    #             cell_info[cellId - 1]['Broadcast_Cell_Open_Voltage'] = cellOpenVoltage
                    #         else:
                    #             print('Clearly something is kinda F##$ed Up')
                    #         #Set temp cell info to zero to make way for next cell
                    #         print(cell_info[cellId - 1])
                    #         cellId          = 0
                    #         cellInstVoltage = 0
                    #         cellResistance  = 0
                    #         cellOpenVoltage = 0   
                            
                           

                           
                             
            except Exception as e:
                print(e)
                

    except:
        print('the bus stopped.. Why did the bus stop? !!')


def populate_whitelist():  
    #The for loop seems to have a problem if a list of CANMessages are appended to another list.
    #The whilelist will have to be once long list with all the needed message IDS
    for message in CANMsgs_Master:   
        if message.id not in WHITELIST_IDs:
            WHITELIST_IDs.append(message.id)
    print(WHITELIST_IDs)
    

#run if this is the main script being run
if __name__ == '__main__':

    populate_whitelist()

    bus_device = None
    bus_thread = None

    try: 
        os.system('sudo ip link set can0 type can bitrate 500000')
        os.system('sudo ifconfig can0 up')
        bus = can.interface.Bus(channel = 'can0', bustype = 'socketcan')# socketcan_native
        #populate the whitelist ID list
        
        # Start the bus reading in the background thread
        bus_thread = threading.Thread(target=bus_run_loop, args=(bus,))
        bus_thread.start()

        #make a test button
        
        
        ws.title('Orion Reader')
        ws.geometry('760x544')
        Btest = tk.Button(ws,text="Send OBD",command = lambda : clear_fault_codes(0x7df))
        Btest.pack()
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

            #destroy the tkinter mainloop
           # ws.destroy()

            #print the exception if the thread returned one
            if thread_exception:
                traceback.print_exception(*thread_exception)
                sys.stderr.flush()
            else:
                print('The bus is being stopped safely')



