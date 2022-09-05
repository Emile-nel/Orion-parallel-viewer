


from ctypes import Structure, c_uint
from operator import le
from tokenize import String
import can
from can.bus import BusState
from can import Message


#OBD2 PID definitions
Orion_PIDs_dict = [
    {
        'name'      :   'relayStatus',
        'units'     :   '',
        'PID'       :   0xF004,
        'OBD2_Mode' :   0x22,
        'length'    :   2,
        'scaling'   :   1,
        'max'       :   65535,
        'min'       :   0
    },
    {
        'name'      :   'relayStatus',
        'units'     :   '',
        'PID'       :   0xF004,
        'OBD2_Mode' :   0x22,
        'length'    :   2,
        'scaling'   :   1,
        'max'       :   65535,
        'min'       :   0
    },
]



class OBD2PID(Structure) :
    
    def __init__(self, name,units,PID,OBD2Mode,MsgLength,scaling,MsgMax,MsgMin):
        self.name       =   name
        self.units      =   units
        self.PID        =   PID
        self.OBD2Mode   =   OBD2Mode 
        self.MsgLength  =   MsgLength
        self.scaling    =   scaling    
        self.MsgMax     =   MsgMax
        self.MsgMin     =   MsgMin   
    
    # _fields_ = [
    #     ('name'      ,   String),
    #     ('units'     ,   String),
    #     ('PID'       ,   int),
    #     ('OBD2_Mode' ,   int),
    #     ('length'    ,   int),
    #     ('scaling'   ,   int),
    #     ('max'       ,   int),
    #     ('min'       ,   int)
    # ]

OrionPID = [
    OBD2PID('relayState','',0xF004,0x22,2,1,65535,0),
    OBD2PID('PackCCL','Amps',0xF00A,0x22,2,1,65535,0),
    OBD2PID('PackDCL','Amps',0xF00B,0x22,2,1,65535,0),
    OBD2PID('PackCurrent','Amps',0xF00C,0x22,2,0.1,32767,-32767),
]


print(OrionPID[0].name)

def receive_all():
    
    """Receives all messages and prints them to the console until Ctrl+C is pressed."""

    with can.interface.Bus(
        bustype="pcan", channel="PCAN_USBBUS1", bitrate=500000
    ) as bus:
        # bus = can.interface.Bus(bustype='ixxat', channel=0, bitrate=250000)
        # bus = can.interface.Bus(bustype='vector', app_name='CANalyzer', channel=0, bitrate=250000)

        # set to read-only, only supported on some interfaces
        bus.state = BusState.PASSIVE

        try:
            while True:
                msg = bus.recv(1)
                for OrionMessage in OrionPID:
                    if msg.arbitration_id == OrionMessage.PID:
                        print()
                if msg is not None:
                    print(msg)

        except KeyboardInterrupt:
            pass  # exit normally


if __name__ == "__main__":
    receive_all()
