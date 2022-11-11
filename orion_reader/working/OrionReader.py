## Needed Imports
from ast import Or
from distutils.log import debug
import re
from PCANBasic import *
import string  
import time
import threading
import os
from PCANOrionReader import *
import dash
from dash import dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import time
from CANManager import ManageCan
from datetime import datetime

OrionPCAN = None
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
CM = ManageCan()
IS_WINDOWS = platform.system() == 'Windows'

global connectAttempt
connectAttempt = 1
connectString = "Still trying to connect. Make sure the device is connected"

#OrionPCAN.GetDataInt

cell_id = 0

def create_battery_card(batteryName,voltage,current,power,soc,isFault,batteryId,isConnected):
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
    if isConnected:
        if isFault:
            statusString = "FAULT"
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
),id=batteryId,n_clicks=0,style={"width":"85%","max-width":"800px","min-width":"700px"})


app.layout = html.Div([
    #main div
    html.Div(       
        className="main-body-temp",
        children=[
            html.Div(id = "connecting_screen"),
            html.Div(id = "battery_cards", children= [html.H5("Summer Breez Battery Monitor"),
            create_battery_card('Orion Master Combined',156.22432,50.2,500,53,False,'master_combined',True),
            create_battery_card('Orion Master',156.22432,50.2,500,53,False,'master',True),
            create_battery_card('Orion Slave1',156.22432,0.12,5000,53,False,'slave1',False),
            create_battery_card('Orion Slave2',156.22432,-50.2,500,53,False,'slave2',True),
            html.Div(id="masterCombinedSelected",children="",),
            html.Div(id="masterSelected",children="",),
            html.Div(id="slave1Selected",children="",),
            #html.Div(id="slave2Selected",children="",),
            ]),
            

    ],style={"display":"none"}
    ),
    html.Div(   
        id = 'main_display', 
        className="main-body",
    ),
    dcc.Interval(
        id = 'interval-component',
        interval=3*1000, # in milliseconds
        #n_intervals=0
    ),
    html.Div(id="slave2Selected",children="afasfasdfadf",style={"background-color": "rgb(35,43,58)"}),


])

@app.callback(Output('main_display', 'children'),
              Input('interval-component', 'n_intervals'))
def render_main(n):
    #Check if CANBus device is initialized and connected
    if CM.isConnected:
        #Check if the CANbus is being read periodically. 
        if CM.isRunning:
            
            onlineStatus = CM.MM.BMS_Master.isOnline
            print(CM.MM.BMS_Master.activeFaults)

            
            #print(datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
            
            
            return [
                create_battery_card('Orion Master Combined',CM.MM.BMS_Master_Combined.instantVoltage,
                CM.MM.BMS_Master_Combined.packCurrent,CM.MM.BMS_Master_Combined.packCurrent*CM.MM.BMS_Master_Combined.instantVoltage,
                CM.MM.BMS_Master_Combined.packSOC,CM.MM.BMS_Master_Combined.isFault,'master_combined',CM.MM.BMS_Master_Combined.isOnline),               
                create_battery_card('Orion Master BMS',CM.MM.BMS_Master.instantVoltage,
                CM.MM.BMS_Master.packCurrent,CM.MM.BMS_Master.packCurrent*CM.MM.BMS_Master.instantVoltage,
                CM.MM.BMS_Master.packSOC,CM.MM.BMS_Master.isFault,'master',CM.MM.BMS_Master.isOnline),
                create_battery_card('Orion Slave1 BMS',CM.MM.BMS_Slave1.instantVoltage,
                CM.MM.BMS_Slave1.packCurrent,CM.MM.BMS_Slave1.packCurrent*CM.MM.BMS_Slave1.instantVoltage,
                CM.MM.BMS_Slave1.packSOC,CM.MM.BMS_Slave1.isFault,'slave1',CM.MM.BMS_Slave1.isOnline),
                create_battery_card('Orion Slave2 BMS',CM.MM.BMS_Slave2.instantVoltage,
                CM.MM.BMS_Slave1.packCurrent,CM.MM.BMS_Slave1.packCurrent*CM.MM.BMS_Slave1.instantVoltage,
                CM.MM.BMS_Slave1.packSOC,CM.MM.BMS_Slave1.isFault,'slave2',CM.MM.BMS_Slave2.isOnline),
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
        
        #return  [create_battery_card('Orion Slave2',0,0,0,0,False,'slave2')]

    
    

# @app.callback(
#     Output("masterCombinedSelected","children"),
#     Input("master_combined","n_clicks"),
# )
# def update_state(n_clicks):
#     return "Master-Combined selected {n} times".format(n=n_clicks)

# @app.callback(
#     Output("masterSelected","children"),
#     Input("master","n_clicks"),
# )
# def update_state(n_clicks):
#     return "Master selected {n} times".format(n=n_clicks)

# @app.callback(
#     Output("slave1Selected","children"),
#     Input("slave1","n_clicks"),
# )
# def update_state(n_clicks):
#     return "Slave 1 selected {n} times".format(n=n_clicks)

@app.callback(
    Output("slave2Selected","children"),
    Input("slave2","n_clicks"),
)
def update_state(n_clicks):
    return "Slave 2 selected {n} times".format(n=n_clicks)




#run if this is the main script being run
if __name__ == '__main__':
    #Start flask app
    app.run_server(debug=False)
    #CM.startCAN()
    ## Reading messages...
    # have some sort of indicatio that the background tasks are indeed running
    #
