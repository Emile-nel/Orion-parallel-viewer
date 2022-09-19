
from mimetypes import init
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
import OrionView

ws = tk.Tk()





stop_bus = threading.Event()

thread_exception = None

can_messages    = {}
cell_info       = {0xe3:[],0xe4:[],0xe5:[],0xe6:[]}
#Create an ampty list for master to slave3 
for u in range(0,4,1):
    for i in range(1,45,1):
        cell_info[0xe3+u].append({'Broadcast_Cell_ID':i,'Broadcast_Cell_Intant_Voltage': 0.0, 'Broadcast_Cell_Resistance': 0.0,'Broadcast_Cell_Open_Voltage' : 0.0})






WHITELIST_IDs = []#[0x3b1,0x3b2,0x3b3] #List of message IDs that we want. 


id_list = [0x3b1,0x3b2,0x3b3]
id_read =[]
msg_list = []



      
#Message list coming from the Master BMS
CANMsgs_Master = [
# CANMessage('Broadcast_Cell_ID',             0xe3,0,8,BitOrder.MSB,ByteOrder.BigEndian,1),  
# CANMessage('Broadcast_Cell_Intant_Voltage', 0xe3,8,16,BitOrder.MSB,ByteOrder.BigEndian,0.1),    #Units in mV
# CANMessage('Broadcast_Cell_Resistance',     0xe3,24,16,BitOrder.MSB,ByteOrder.BigEndian,0.01),  #Units in mOhm 
# CANMessage('Broadcast_Cell_Open_Voltage',   0xe3,40,16,BitOrder.MSB,ByteOrder.BigEndian,0.1),   #Units in mV
    #0x3b1
OrionView.CANMessage('Master_Pack_Current',                       0x3b1,0,16,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,0.1),
OrionView.CANMessage('Master_Inst_Voltage',                       0x3b1,16,16,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,0.1),
OrionView.CANMessage('Master_Pack_SOC',                           0x3b1,32,8,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,0.5),
OrionView.CANMessage('Master_Relay_State',                        0x3b1,40,8,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1),
    #0x3b2
OrionView.CANMessage('Master_Pack_DCL',                           0x3b2,0,16,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1),
OrionView.CANMessage('Master_Pack_CCL',                           0x3b2,16,8,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1),
OrionView.CANMessage('Master_High_Temperature',                   0x3b2,32,8,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1),
OrionView.CANMessage('Master_Low_Temperature',                    0x3b2,40,8,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1),
    #0x3b3 - unit error messages
OrionView.CANMessage('DTC P0A1F : Internal Cell Communication',   0x3b3,0,1,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1), 
OrionView.CANMessage('DTC P0A12 : Cell Balancing Stuck Off',      0x3b3,1,1,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1),
OrionView.CANMessage('DTC P0A80 : Weak Cell',                     0x3b3,2,1,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1),
OrionView.CANMessage('DTC P0AFA : Low Cell Voltage',              0x3b3,3,1,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1),
OrionView.CANMessage('DTC P0A04 : Cell Open Wiring',              0x3b3,4,1,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1),
OrionView.CANMessage('DTC P0AC0 : Current Sensor',                0x3b3,5,1,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1),
OrionView.CANMessage('DTC P0A0D : Cell Voltage Over 5V',          0x3b3,6,1,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1),
OrionView.CANMessage('DTC P0A0F : Cell Bank',                     0x3b3,7,1,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1),
OrionView.CANMessage('DTC P0A02 : Weak Pack',                     0x3b3,8,1,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1),
OrionView.CANMessage('DTC P0A81 : Fan Monitor',                   0x3b3,9,1,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1),
OrionView.CANMessage('DTC P0A9C : Thermistor',                    0x3b3,10,1,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1),
OrionView.CANMessage('DTC U0100 : CAN Communication',             0x3b3,11,1,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1),
OrionView.CANMessage('DTC P0560 : Redundant Power Supply',        0x3b3,12,1,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1),
OrionView.CANMessage('DTC P0AA6 : High Voltage Isolation',        0x3b3,13,1,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1),
OrionView.CANMessage('DTC P0A05 : Invalid Input Supply Voltage',  0x3b3,14,1,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1),  
OrionView.CANMessage('DTC P0A06 : ChargeEnable Relay',            0x3b3,15,1,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1), 
OrionView.CANMessage('DTC P0A07 : DischargeEnable Relay',         0x3b3,16,1,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1), 
OrionView.CANMessage('DTC P0A08 : Charger Safety Relay',          0x3b3,17,1,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1), 
OrionView.CANMessage('DTC P0A09 : Internal Hardware',             0x3b3,18,1,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1), 
OrionView.CANMessage('DTC P0A0A : Internal Heatsink Thermistor',  0x3b3,19,1,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1), 
OrionView.CANMessage('DTC P0A0B : Internal Logic',                0x3b3,20,1,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1), 
OrionView.CANMessage('DTC P0A0C : Highest Cell Voltage Too High', 0x3b3,21,1,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1), 
OrionView.CANMessage('DTC P0A0E : Lowest Cell Voltage Too Low',   0x3b3,22,1,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1), 
OrionView.CANMessage('DTC P0A10 : Pack Too Hot',                  0x3b3,23,1,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1), 
OrionView.CANMessage('Balancing_Active',                          0x3b3,24,1,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1), 
OrionView.CANMessage('MultiPurpose_Enable',                       0x3b3,25,1,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1), 
OrionView.CANMessage('Charge Enable Inverted',                    0x3b3,26,1,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1),
    #0x3b3 - Parallel string specific error messages
OrionView.CANMessage('Parallel Combined Charge Enable Inverted',  0x3b3,30,1,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1), 
OrionView.CANMessage('Parallel Combined Faults Present',          0x3b3,31,1,OrionView.BitOrder.MSB,OrionView.ByteOrder.BigEndian,1), 

]

def process_cell_broadcast(messageId,messageData):
    
        #Extract the cell ID
        cellId          = messageData[0]
        #Extract instant voltage in mV
        valueInts       = messageData[1:3]
        ValueBytes      = bytes(valueInts)
        cellInstVoltage = int.from_bytes(ValueBytes,"big")*0.1
        #Extract Cell resistance in mOhm
        valueInts       = messageData[3:5]
        ValueBytes      = bytes(valueInts)
        cellResistance  = int.from_bytes(ValueBytes,"big")*0.01
        #Extract Cell Open Voltage in mV
        valueInts       = messageData[5:7]
        ValueBytes      = bytes(valueInts)
        cellOpenVoltage = int.from_bytes(ValueBytes,"big")*0.1
        #Append cell info list for master unit
        cell_info[messageId][cellId - 1]['Broadcast_Cell_ID'] = cellId
        cell_info[messageId][cellId - 1]['Broadcast_Cell_Intant_Voltage'] = cellInstVoltage
        cell_info[messageId][cellId - 1]['Broadcast_Cell_Resistance'] = cellResistance
        cell_info[messageId][cellId - 1]['Broadcast_Cell_Open_Voltage'] = cellOpenVoltage



def clear_fault_codes(unitId):
    #use unitId of 0x7df to clear DTC faults on all units
    #0x7e3 - Master
    #0x7e4 - Slave1
    #0x7e5 - Slave2
    #0x7e6 - Slave3

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
                
                #Process cell broadcast message. 
                cell_broadcast_ids = [0xe3,0xe4,0xe5,0xe6] 
                if messageId in cell_broadcast_ids:
                    process_cell_broadcast(messageId,messageData)
                      

               #Check if can ID is in whitelist and do some stuff with it if it is. Else, leave it alone
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



