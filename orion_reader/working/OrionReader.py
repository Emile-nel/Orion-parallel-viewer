## Needed Imports
from ast import Or
from distutils.log import debug

from PCANBasic import *

from PCANOrionReader import *
import dash
from dash import dcc, ctx
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from CANManager import ManageCan
from datetime import datetime
from CANManager import BMSUnit


OrionPCAN = None
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
CM = ManageCan()
IS_WINDOWS = platform.system() == 'Windows'



global connectAttempt
connectAttempt = 1
connectString = "Still trying to connect. Make sure the device is connected"

class displayParameters():

    masterCombinedSelected = False
    masterSelected = False
    slave1Selected = False
    slave2Selected = False
    slave3Selected = False

#OrionPCAN.GetDataInt

DP = displayParameters()

cell_id = 0

def get_active_alarms(BMS:BMSUnit):
    activeAlarmList = BMS.get_alarm_history()
    #print(activeAlarmList)
    rowList =[
        #add header
        dbc.Row(
                className="info_row row justify-content-between",
                children=[
                    dbc.Col("Error Description", className="col-md-8 info_name"),
                    dbc.Col("Date Raised",className="col-md-4 info_name", style={"text-align": "center"}),
                ]
                ),
    ]
    
   
    for alarm in activeAlarmList:
        #print(alarm)

        alarmRow =  dbc.Row(
                        className="info_row row justify-content-between",
                        children=[
                            dbc.Col("{}".format(alarm[1]), className="col-md-7 info_name"),
                            dbc.Col("{}".format(alarm[0]),className="col-md-5 info_name", style={"text-align": "end"}),
                        ]
                )
        rowList.append(alarmRow)
    return rowList
            
    
def create_battery_info(BMS : BMSUnit):

    
    voltage = BMS.instantVoltage
    soc = BMS.packSOC
    current = BMS.packCurrent
    power = voltage*current
    #print("this is the battery info card")
    if BMS.isOnline:
        if BMS.isFault:
            statusString = "FAULT"
            statusStyle = { "height":"50%", "color" : "red"}
        elif not BMS.relayState:
            statusString = "RELAY\nOPEN"
            statusStyle = { "height":"50%", "color" : "red"}          
        else:
            statusString = "OK"
            statusStyle = { "height":"50%", "color" : "green"}
    else:
        statusString = "CONN.\nERROR"
        statusStyle = { "height":"50%", "color" : "red"}     

    return html.Div(className="battery_info width_constraint",children=[
        #State
        dbc.Row(
            className="info_row row justify-content-between",
            children=[
                dbc.Col("Status", className="col-md-8 info_name"),
                dbc.Col(className="col-md-4 info_name", 
                children = [
                    dbc.Row(
                    className="row justify-content-end",
                    children=[
                        dbc.Col("{}".format(statusString),className="col-md-4 info_value "),
                    ]
                )
                ]),

            ]
        ),
        #Battery
        dbc.Row(
            className="info_row row justify-content-between",
            children=[
                dbc.Col("Battery Summary", className="col-md-8 info_name"),
                dbc.Col(className="col-md-4 info_name", 
                children = [
                    dbc.Row(
                    className="row justify-content-end gx-1",
                    children=[
                        dbc.Col("{:.1f} V".format(voltage),className="col info_value"),
                        dbc.Col("{:.1f} A".format(current),className="col info_value"),
                        dbc.Col("{:.0f} W".format(power),className="col info_value"),
                    ]
                )
                ]),
                
                
            ]
        ),        
        #State of Charge
        dbc.Row(
            className="info_row row justify-content-between",
            children=[
                dbc.Col("State Of Charge (SOC)", className="col-md-8 info_name"),
                dbc.Col(className="col-md-4 info_name", 
                children = [
                    dbc.Row(
                    className="row justify-content-end",
                    children=[
                        dbc.Col("{:.1f} %".format(soc),className="col info_value"),
                    ]
                )
                ]),
                
                
            ]
        ),  
        #Battery Temperature [highest]
        dbc.Row(
            className="info_row row justify-content-between",
            children=[
                dbc.Col("Battery High Temp", className="col-md-8 info_name"),
                dbc.Col(className="col-md-4 info_name", 
                children = [
                    dbc.Row(
                    className="row justify-content-end",
                    children=[
                        dbc.Col("{:.1f} \N{DEGREE SIGN}C".format(BMS.highTemp),className="col info_value"),
                        
                    ]
                )
                ]),
            ]
        ),
        #Consumed amphours ? 
        #Details
        dbc.Row(
            className="info_row row justify-content-between",
            children=[
                dbc.Col("Details", className="col-md-8 info_name"),
                dbc.Col(className="col-md-4 info_name", 
                children = [
                    dbc.Row(
                    className="row justify-content-end",
                    children=[
                        dbc.Col("BTN",className="col info_value"),
                    ]
                )
                ]),
            ]
        ),
            #lowest Cell [cell : voltage]
            #Highest Cell [cell : voltage]
            #min Temp [cell : temp]
            #max temp [cell : temp]
            #Battery Modules 
            #Installed capacity
            #Balancing ? 
        #Active Alarms
        dbc.Row(
            className="info_row row justify-content-between",
            children=[
                dbc.Col("Active Alarms", className="col-md-8 info_name"),
                dbc.Col(className="col-md-4 info_name", 
                children = [
                    dbc.Row(
                    className="row justify-content-end",
                    children=[
                        dbc.Col("BTN",className="col info_value"),
                    ]
                )
                ]),
            ]
        ),
        #Alarm history
        dbc.Row(
            className="info_row row justify-content-between",
            children=[
                dbc.Col("Alarms History", className="col-md-8 info_name"),
                dbc.Col(className="col-md-4 info_name", 
                children = [
                    dbc.Row(
                    className="row justify-content-end",
                    children=[
                        dbc.Col("BTN",className="col info_value"),
                    ]
                )
                ]),
            ]
        ),
        #Battery History
        dbc.Row(
            className="info_row row justify-content-between",
            children=[
                dbc.Col("Battery History", className="col-md-8 info_name"),
                dbc.Col(className="col-md-4 info_name", 
                children = [
                    dbc.Row(
                    className="row justify-content-end",
                    children=[
                        dbc.Col("BTN",className="col info_value"),
                    ]
                )
                ]),
            ]
        ),
        #IO
        dbc.Row(
            className="info_row row justify-content-between",
            children=[
                dbc.Col("IO Conditions", className="col-md-8 info_name"),
                dbc.Col(className="col-md-4 info_name", 
                children = [
                    dbc.Row(
                    className="row justify-content-end",
                    children=[
                        dbc.Col("BTN",className="col info_value"),
                    ]
                )
                ]),
            ]
        ),
        #Cell Info
        dbc.Row(
            className="info_row row justify-content-between",
            children=[
                dbc.Col("Cell Info", className="col-md-8 info_name"),
                dbc.Col(className="col-md-4 info_name", 
                children = [
                    dbc.Row(
                    className="row justify-content-end",
                    children=[
                        dbc.Col("BTN",className="col info_value"),
                    ]
                )
                ]),
            ]
        ),
        html.Div(children=get_active_alarms(BMS)),


        
        

        
    ]
        
    )
        
        

    

def create_battery_card(BMS : BMSUnit, batteryId : str ):
    #batteryName,voltage,current,power,soc,isFault,batteryId,isConnected
    batteryName = BMS.BMSName
    voltage = BMS.instantVoltage
    soc = BMS.packSOC
    isFault = BMS.isFault
    isOnline = BMS.isOnline
    current = BMS.packCurrent
    power = voltage*current

     


    if power < 1000 :
        power_string = '{power:.1f} W'.format(power=power)
    else:
        power_string = '{power:.1f} kw'.format(power=power/1000)

    if -1 < current < 1:#in idle
        soc_string = '{soc} % idle'.format(soc=soc)
    if current >= 1: #Charging
        soc_string = '{soc} % charging'.format(soc=soc)
    if current <= -1: # Discharging
        soc_string = '{soc} % discharging'.format(soc=soc)
    if isOnline:
        if isFault:
            statusString = "FAULT"
            statusStyle = { "height":"50%", "color" : "red"}
        elif not BMS.relayState:
            statusString = "RELAY\nOPEN"
            statusStyle = { "height":"50%", "color" : "red"}          
        else:
            statusString = "OK"
            statusStyle = { "height":"50%", "color" : "green"}
    else:
        statusString = "CONN.\nERROR"
        statusStyle = { "height":"50%", "color" : "red"}     

    return html.Div(dbc.Container( 
    [
        dbc.Row(
            
            [
                dbc.Col(className="col-md-2 ",
                children=[html.Img(src="/assets/images/batery_icon.png")]),
                dbc.Col(className="col-md-8",
                children=[
                    html.Div('{name}'.format(name=batteryName)),
                    dbc.Row(
                        children=[
                        dbc.Col(className="col-md-3",children=[html.Div("{voltage:.2f} V".format(voltage=voltage))]),
                        dbc.Col(className="col-md-3",children=[html.Div("{current:.2f} A".format(current=current))]),
                        dbc.Col(className="col-md-3",children=[html.Div("{sPower}".format(sPower=power_string))]),
                        dbc.Col(className="col-md-3",children=[html.Div('{sSoc}'.format(sSoc=soc_string))]),]
                    )
                ]),
                dbc.Col(className="col-md-2 battery-status  d-flex flex-column justify-content-center",
                    children=[
                        
                                html.H6("Status", className="p-2", style={ "height":"50%"}),
                                html.H5(statusString, className="p-2", style=statusStyle)                        
                            ]),
            ],className="battery-tile align-items-center text-start ",
        )
    ], className="justify-content-center"
),id=batteryId,n_clicks=0, className="width_constraint" )
    
    

app.layout = html.Div([
    #main div
    
    html.Div(   
        id = 'main_display', 
        className="main-body",
    ),
    html.Button('Reset BMSs',id='bms_reset',n_clicks=0),
    html.Div("this is where the text goes", id="test_text"),
    html.Button('Submit', id='submit-val', n_clicks=0),
    html.Div(   
        id = 'test_div', 
        
    ),


    dcc.Interval(
        id = 'interval-component',
        interval=3*1000, # in milliseconds
        #n_intervals=0
    ),
    # html.Div(   
    #     id = 'battery_info_page', 
        
    # ),

   

    
    


])





@app.callback(Output('main_display', 'children'),
                [
                    Input('interval-component', 'n_intervals'),
                    
                    

                    # Input("master_combined","n_clicks"),
                    # Input("master","n_clicks"),
                    # Input("slave1","n_clicks"),
                    # Input("slave2","n_clicks"),

                ],
                prevent_initial_call=True,
)


              
#def render_main(n,n_master_combined,n_master,n_slave1,n_slave2):
def render_main(n):
    #Check if CANBus device is initialized and connected
    if CM.isConnected:
        #Check if the CANbus is being read periodically. 
        if CM.isRunning:
            
            onlineStatus = CM.MM.BMS_Master.isOnline
            #print("Master has a fault : {}".format(CM.MM.BMS_Master.isFault))
           # print(CM.MM.BMS_Master.cell_info[0])



            # #check if a battery was selected
            # if n_master_combined > 0:
            #     DP.masterCombinedSelected = True
            #     infoBMS = CM.MM.BMS_Master_Combined
            #     n_master_combined = 0 #Set to zero to avoid a loop
            # if n_master > 0:
            #     DP.masterCombinedSelected = True
            #     infoBMS = CM.MM.BMS_Master_Combined
            #     n_master = 0 #Set to zero to avoid a loop
            # if n_slave1> 0:
            #     DP.masterCombinedSelected = True
            #     infoBMS = CM.MM.BMS_Master_Combined
            #     n_slave1 = 0 #Set to zero to avoid a loop
            # if n_slave2 > 0:
            #     DP.masterCombinedSelected = True
            #     infoBMS = CM.MM.BMS_Master_Combined
            #     n_slave2 = 0 #Set to zero to avoid a loop

            #Check that more than one battery was selected. If so, make all false to avoid crashing
            # if (int(DP.masterCombinedSelected) + int(DP.masterSelected) + int(DP.slave1Selected) + int(DP.slave2Selected) + int(DP.slave3Selected)) > 1:
            #     DP.masterCombinedSelected = False
            #     DP.masterSelected = False
            #     DP.slave1Selected = False
            #     DP.slave2Selected = False
            #     DP.slave3Selected = False

            
            # if DP.masterCombinedSelected or DP.masterSelected or DP.slave1Selected or DP.slave2Selected or DP.slave3Selected:
            #     if n_info > 0 : #back button
            #         n_info = 0 #Avoid loops
            #         DP.masterCombinedSelected = False
            #         DP.masterSelected = False
            #         DP.slave1Selected = False
            #         DP.slave2Selected = False
            #         DP.slave3Selected = False        
            if DP.masterCombinedSelected :
                print("Something")
                
            else:
                return [
                                  # Input("master_combined","n_clicks"),
                    # Input("master","n_clicks"),
                    # Input("slave1","n_clicks"),
                    # Input("slave2","n_clicks"),
                    create_battery_card(CM.MM.BMS_Master_Combined,"master_combined"),               
                    create_battery_card(CM.MM.BMS_Master,"master"),
                    create_battery_card(CM.MM.BMS_Slave1,"slave1"),
                    create_battery_card(CM.MM.BMS_Slave2,"slave2"),
                    create_battery_info(CM.MM.BMS_Master),
                    
                    
                    # html.Div("Master Combined selected {n} times".format(n=n_master_combined)),
                    # html.Div("Master  selected {n} times".format(n=n_master)),
                    # html.Div("Slave1  selected {n} times".format(n=n_slave1)),
                    # html.Div("Slave2  selected {n} times".format(n=n_slave2)),

                    ]
        else: 
            print("Start reading timer")
            CM.startCANBusRead()

        
    else:
        connectStringTemp = ""
        if CM.startCANDevice():
            print("CANBus started successfully")
            connectStringTemp = "CANBus connection successful ! "
        else:
            # connectAttempt = connectAttempt + 1
            # connectStringTemp = connectString
            # for x in range(0,connectAttempt):
            #     connectStringTemp = connectStringTemp + "."
            # if connectAttempt == 10:
            #     connectAttempt = 1
            # print(connectStringTemp)
            print("still trying to connect")
            connectStringTemp = "Trying to connect to CANBus \n Make sure the device is connected properly."
        print("____________####_____still trying to connect____######__________")
        return html.Span(className="loading_screen",children=["{s}".format(s=connectStringTemp)])
        
     
@app.callback(Output('test_div', 'children'),
                [
                    Input("master_combined","n_clicks"),
                    Input("master","n_clicks"),
                    Input("slave1","n_clicks"),
                    Input("slave2","n_clicks"),
                    Input("submit-val","n_clicks"),
                ],
                prevent_initial_call=True,
)


              
#def render_main(n,n_master_combined,n_master,n_slave1,n_slave2):
def battery_click(n_MC,n_M,n_S1,n_S2,sv):
    #print("Call back triggered")
    ts = {"color":"black"}
    if n_MC > 0:
        print("master has been clicked")

    return [        html.Div("Master Combined selected {n} times".format(n=sv), style=ts),
                    html.Div("Master  selected {n} times".format(n=n_M), style=ts),
                    html.Div("Slave1  selected {n} times".format(n=n_S1), style=ts),
                    html.Div("Slave2  selected {n} times".format(n=n_S2), style=ts),]
                    



              
#def render_main(n,n_master_combined,n_master,n_slave1,n_slave2):
    
#reset all bmss
@app.callback(
    Output('test_text','children'),
    Input('bms_reset','n_clicks'),
    prevent_initial_call=True,
    )
    

def call_bms_reset(n_clicks):
    #print("reset button pressed")
    CM.BMSResetAll()


#run if this is the main script being run
if __name__ == '__main__':
    #Start flask app
    app.run_server(debug=True)
    #CM.startCAN()
    ## Reading messages...
    # have some sort of indicatio that the background tasks are indeed running
    #
