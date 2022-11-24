
from enum import Enum




class BitOrder(Enum):
    LSB = 0
    MSB = 1

class ByteOrder(Enum):
    LittleEndian = "little"
    BigEndian = "big"



class BMSUnit:
    def __init__(self,
    unitType        = 0,# = master, 1= slave
    instantVoltage  = 0,
    packCurrent     = 0,
    packSOC         = 0,
    packDCL         = 0,
    packCCL         = 0,
    relayState      = False,
    isFault         = False,
    allowCharge     = False,
    faultList       = {
        'DTC P0A1F : Internal Cell Communication'   :   False,  
        'DTC P0A12 : Cell Balancing Stuck Off'      :   False,      
        'DTC P0A80 : Weak Cell'                     :   False,                    
        'DTC P0AFA : Low Cell Voltage'              :   False,             
        'DTC P0A04 : Cell Open Wiring'              :   False,             
        'DTC P0AC0 : Current Sensor'                :   False,               
        'DTC P0A0D : Cell Voltage Over 5V'          :   False,         
        'DTC P0A0F : Cell Bank'                     :   False,                    
        'DTC P0A02 : Weak Pack'                     :   False,                    
        'DTC P0A81 : Fan Monitor'                   :   False,                        
        'DTC P0A9C : Thermistor'                    :   False,                   
        'DTC U0100 : CAN Communication'             :   False,            
        'DTC P0560 : Redundant Power Supply'        :   False,       
        'DTC P0AA6 : High Voltage Isolation'        :   False,       
        'DTC P0A05 : Invalid Input Supply Voltage'  :   False, 
        'DTC P0A06 : ChargeEnable Relay'            :   False,           
        'DTC P0A07 : DischargeEnable Relay'         :   False,        
        'DTC P0A08 : Charger Safety Relay'          :   False,         
        'DTC P0A09 : Internal Hardware'             :   False,            
        'DTC P0A0A : Internal Heatsink Thermistor'  :   False, 
        'DTC P0A0B : Internal Logic'                :   False,               
        'DTC P0A0C : Highest Cell Voltage Too High' :   False,
        'DTC P0A0E : Lowest Cell Voltage Too Low'   :   False,  
        'DTC P0A10 : Pack Too Hot'                  :   False,                 
    },
    highCellVoltage = 0,
    highCellId      = 0,
    lowCellVoltage  = 0,
    lowCellId       = 0,
    isBalancing     = False,
    highTemp        = 0,
    lowTemp         = 0,
    heatSinkTemp    = 0,
    lastOnline      = None,
       ) -> None:
        self.unitType           = unitType          ,
        self.instantVoltage     = instantVoltage    ,
        self.packCurrent        = packCurrent       ,
        self.packSOC            = packSOC           ,
        self.packDCL            = packDCL           ,
        self.packCCL            = packCCL           ,
        self.relayState         = relayState        ,
        self.isFault            = isFault           ,
        self.allowCharge        = allowCharge       ,
        self.faultList          = faultList         ,
        self.highCellVoltage    = highCellVoltage   ,
        self.highCellId         = highCellId        ,
        self.lowCellVoltage     = lowCellVoltage    ,
        self.lowCellId          = lowCellId         ,
        self.isBalancing        = isBalancing       ,
        self.highTemp           = highTemp          ,
        self.lowTemp            = lowTemp           ,
        self.heatSinkTemp       = heatSinkTemp      ,
        self.lastOnline         = lastOnline        ,

    def set_val(self,name,value):
        #Grab and store BMS Unit values
       
        if name == 'Pack_Current':
            self.instantVoltage = value                     
        elif name == 'Inst_Voltage'   :                      
            self.packCurrent    = value  
        elif name == 'Pack_SOC'   :                          
            self.packSOC        = value  
        elif name == 'Relay_State'    :   
            self.packSOC        = value                    
        elif name == 'Pack_DCL'   :
            self.packDCL        = value                         
        elif name == 'Pack_CCL'   : 
            self.packCCL        = value                    
        elif name == 'High_Temperature'   :                  
            self.highTemp       = value
        elif name == 'Low_Temperature'    :                                   
            self.lowTemp        = value
        elif name == 'Balancing_Active'  :                         
            self.isBalancing    = value
        elif name == 'MultiPurpose_Enable'   :                      
            self.relayState     = value
        elif name == 'Charge Enable Inverted'    :                   
            self.allowCharge    = value
           
        #BMS fault handling
        faultKeys = list(self.faultList.keys)
        if name in faultKeys:
            self.faultList[name] = value
            if value:
                self.isFault = True
        #clear isfault if none of the faults are present anymore
        if self.isFault:
            isFaultCheck = False
            for key in faultKeys:
                isFaultCheck = isFaultCheck & self.faultList[key]


class CombinedBMSUnit(BMSUnit):
    def __init__(self,) -> None:
        pass

class CANMessage:

    def __init__(self, 
    name, 
    id,
    startBit,
    len=8,
    bitOrder=BitOrder.MSB,
    byteOrder=ByteOrder.BigEndian,
    factor=1,
    value=None, 
    timeStamp =None):
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

class MessageManager():

    cell_broadcast_ids = [0xe3,0xe4,0xe5,0xe6]
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
    CANMessage('Pack_Current',                              0x3b1,0,16,BitOrder.MSB,ByteOrder.BigEndian,0.1),
    CANMessage('Inst_Voltage',                              0x3b1,16,16,BitOrder.MSB,ByteOrder.BigEndian,0.1),
    CANMessage('Pack_SOC',                                  0x3b1,32,8,BitOrder.MSB,ByteOrder.BigEndian,0.5),
    CANMessage('Relay_State',                               0x3b1,40,8,BitOrder.MSB,ByteOrder.BigEndian,1),
    CANMessage('Pack_DCL',                                  0x3b2,0,16,BitOrder.MSB,ByteOrder.BigEndian,1),
    CANMessage('Pack_CCL',                                  0x3b2,16,8,BitOrder.MSB,ByteOrder.BigEndian,1),
    CANMessage('High_Temperature',                          0x3b2,32,8,BitOrder.MSB,ByteOrder.BigEndian,1),
    CANMessage('Low_Temperature',                           0x3b2,40,8,BitOrder.MSB,ByteOrder.BigEndian,1),
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
    CANMessage('Parallel Combined Charge Enable Inverted',  0x3b3,30,1,BitOrder.MSB,ByteOrder.BigEndian,1), 
    CANMessage('Parallel Combined Faults Present',          0x3b3,31,1,BitOrder.MSB,ByteOrder.BigEndian,1), 
    #parallel bus voltage
    #parallel current
    #parallel charge anable
    #parallel dcl
    #parallel ccl
    #parallel high temp
    #parallel low temp
    #parallel high cell 
    #parallel low cell

    ]    
    WHITELIST_IDs = []#List of message IDs that we want. 

    cell_info       = {0xe3:[],0xe4:[],0xe5:[],0xe6:[]}
    cell_broadcast_ids = [0xe3,0xe4,0xe5,0xe6] 

    BMS_Master = BMSUnit()
    BMS_Slave1 = BMSUnit()
    BMS_Slave2 = BMSUnit()
    BMS_Slave3 = BMSUnit()

    def __init__(self) -> None:
        #populate the whitelists
        self.populate_whitelist()

    def populate_whitelist(self):  
        #The for loop seems to have a problem if a list of CANMessages are appended to another list.
        #The whilelist will have to be once long list with all the needed message IDS
        for message in self.CANMsgs_Master:   
            if message.id not in self.WHITELIST_IDs:
                self.WHITELIST_IDs.append(message.id)
        print(self.WHITELIST_IDs)
            #Create an ampty list for master to slave3 
        for u in range(0,4,1):
            for i in range(1,45,1):
                self.cell_info[0xe3+u].append({'Broadcast_Cell_ID':i,'Broadcast_Cell_Intant_Voltage': 0.0, 'Broadcast_Cell_Resistance': 0.0,'Broadcast_Cell_Open_Voltage' : 0.0})

        
    def process_message(self,messageId,messageData,messageTime):
        if messageId in self.cell_broadcast_ids:
            self.process_cell_broadcast(messageId,messageData)
        elif messageId in self.WHITELIST_IDs:
            for msg in self.CANMsgs_Master:
                if messageId == msg.id:
                    msg.set_val(messageData,messageTime)
                    print(msg.id)
                    print(msg.name)
                    print(msg.value)


    def process_cell_broadcast(self,messageId,messageData):
    
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
        self.cell_info[messageId][cellId - 1]['Broadcast_Cell_ID'] = cellId
        self.cell_info[messageId][cellId - 1]['Broadcast_Cell_Intant_Voltage'] = cellInstVoltage
        self.cell_info[messageId][cellId - 1]['Broadcast_Cell_Resistance'] = cellResistance
        self.cell_info[messageId][cellId - 1]['Broadcast_Cell_Open_Voltage'] = cellOpenVoltage

