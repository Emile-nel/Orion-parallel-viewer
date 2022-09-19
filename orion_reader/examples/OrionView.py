


class BitOrder(Enum):
    LSB = 0
    MSB = 1

class ByteOrder(Enum):
    LittleEndian = "little"
    BigEndian = "big"


class BMSInfo:
    def __init__(self,
    unitType        = 0,# = master, 1= slave
    instantVoltage  = 0,
    packCurrent     = 0,
    packSOC         = 0,
    packDCL         = 0,
    packCCL         = 0,
    relayState      = False,
    isFault         = False,
    faultList       = [],
    highCellVoltage = 0,
    highCellId      = 0,
    lowCellVoltage  = 0,
    lowCellId       = 0,
    highTemp        = 0,
    lowTemp         = 0,
    heatSinkTemp    = 0,
    lastOnline      = None,
       ) -> None:
        self.instantVoltage     = instantVoltage ,
        self.packCurrent        = packCurrent    ,
        self.packSOC            = packSOC        ,
        self.relayState         = relayState     ,
        self.isFault            = isFault        ,
        self.faultList          = faultList      ,
        self.highCellVoltage    = highCellVoltage,
        self.highCellId         = highCellId     ,
        self.lowCellVoltage     = lowCellVoltage ,
        self.lowCellId          = lowCellId      ,
        self.highTemp           = highTemp       ,
        self.lowTemp            = lowTemp        ,
        self.heatSinkTemp       = heatSinkTemp   ,
        self.lastOnline         = lastOnline     ,

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
