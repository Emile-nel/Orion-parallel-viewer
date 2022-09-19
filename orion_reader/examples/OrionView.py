
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
        match name:
            case 'Pack_Current'   :
                self.instantVoltage = value                     
            case 'Inst_Voltage'   :                      
                self.packCurrent    = value  
            case 'Pack_SOC'   :                          
                self.packSOC        = value  
            case 'Relay_State'    :   
                self.packSOC        = value                    
            case 'Pack_DCL'   :
                self.packDCL        = value                         
            case 'Pack_CCL'   : 
                self.packCCL        = value                    
            case 'High_Temperature'   :                  
                self.highTemp       = value
            case 'Low_Temperature'    :                                   
                self.lowTemp        = value
            case 'Balancing_Active'  :                         
                self.isBalancing    = value
            case 'MultiPurpose_Enable'   :                      
                self.relayState     = value
            case 'Charge Enable Inverted'    :                   
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
    def __init__(self,combinedDCL,combinedCCL,) -> None:
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
