## Needed Imports
from ast import Or
from distutils.log import debug
import time
from PCANBasic import *


import dash
from dash import dcc, ctx
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from CANManager import ManageCan
from datetime import datetime
from CANManager import BMSUnit
from pages.battery_info import create_battery_info
from pages.active_alarms import create_active_alarms
from pages.battery_card import create_battery_card
from pages.historic_alarms import create_alarm_history
from pages.io_conditions import create_io_conditions
#from pages.combined_info import create_combined_info
from pages.parallel_battery_card import create_parallel_battery_card



OrionPCAN = None
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
CM = ManageCan()
IS_WINDOWS = platform.system() == 'Windows'



global connectAttempt
connectAttempt = 1
connectString = "Still trying to connect. Make sure the device is connected"

class displayParameters():

    BMSSelected  = BMSUnit
    menuLevel = 0
    tilesSelected = False
    infoSelected = False
    detailsSelected = False
    activeAlarmsSelected = False
    alarmsHistorySelected = False
    batteryHistorySelected = False
    IOSelected = False
    cellInfoSelected = False
    



#OrionPCAN.GetDataInt

DP = displayParameters()

#set initial BMS 
DP.BMSSelected = CM.MM.BMS_Master

cell_id = 0
 
def load_tiles(batteryTileStyle, show : bool):
    """ returns a list of all the battery tiles """

    return html.Div(style=batteryTileStyle, children=[
            create_parallel_battery_card(CM.MM.BMS_Master_Combined,"master_combined"),               
            create_battery_card(CM.MM.BMS_Master,"master"),
            create_battery_card(CM.MM.BMS_Slave1,"slave1"),
            create_battery_card(CM.MM.BMS_Slave2,"slave2"),
            
        ])

    
    
    

app.layout = html.Div([
    #main div
    
    html.Div(   
        id = 'main_display', 
        className="main-body",
        children=[
                load_tiles({'display':'none'},False),
                html.Div(style={'display':'none'}, children=[
                
                    create_battery_info(CM.MM.BMS_Master),
                ])
        ]
    ),
    #dummy buttons to trick dash
    html.Button('Reset BMSs',id='bms_reset',n_clicks=0,style={'display':'none'}),
    html.Button('BACK BUTTOn',id='back_btn',n_clicks=0,style={'display':'none'}),



    dcc.Interval(
        id = 'interval-component',
        #Not running CSGO or anything to just over 1hz should be good. 
        interval=0.5*1000, # in milliseconds
        #n_intervals=0
    ),


])





@app.callback(  
                    Output('main_display', 'children'),
                    
                [
                    Input('interval-component', 'n_intervals'),
                    Input("master_combined","n_clicks"),
                    Input("master","n_clicks"),
                    Input("slave1","n_clicks"),
                    Input("slave2","n_clicks"),
                    Input("back_btn","n_clicks"),
                    Input("cell_info_btn","n_clicks"),
                    Input("details_btn","n_clicks"),
                    Input("active_alarms_btn","n_clicks"),
                    Input("alarms_history_btn","n_clicks"),
                    Input("battery_history_btn","n_clicks"),
                    Input("IO_cond_btn","n_clicks"),
                    Input("bms_reset","n_clicks"),

                ],
                prevent_initial_call=True,
)
            
#def render_main(n,n_master_combined,n_master,n_slave1,n_slave2):
def render_main(n, MC_n, M_n, S1_n, S2_n, back_n,cell_info_n,details_n,active_alarms_n,alarms_history_n,battery_history_n,IO_cond_n,reset_n):
    loadingScreenStyle = {'display':'none', 'width':'100%'}
    resetTileStyle = {'display':'none'}
    batteryTileStyle = {'display':'none'}
    backTileStyle = {'display':'none'}
    batteryinfoCombinedStyle = {'display':'none'}
    batteryinfoStyle = {'display':'none'}
    batteryDetailsCombinedStyle = {'display':'none'}
    batteryDetailsStyle = {'display':'none'}
    cellInfoStyle = {'display':'none'}
    alarmHistoryStyle = {'display':'none'}
    activeAlarmStyle = {'display':'none'}
    IOConditionsStyle = {'display':'none'}

    isFaultActive = CM.MM.BMS_Master.isFault or CM.MM.BMS_Slave1.isFault or CM.MM.BMS_Slave2.isFault
    if isFaultActive:
        resetTileStyle = {'display':'block'}
        if reset_n:
            print("reset button pressed")
            CM.BMSResetAll()
    else:
        resetTileStyle = {'display':'none'}
    if CM.isConnected:
        #Check if the CANbus is being read periodically. 
        if CM.isRunning:
          

            if DP.menuLevel == 0:
                DP.tilesSelected = True
                batteryTileStyle = {'display':'block'}
                batteryinfoStyle = {'display':'none'}
                if  MC_n:
                    print("combined selected")
                    DP.menuLevel = 1
                    DP.BMSSelected = CM.MM.BMS_Master_Combined
                    DP.infoSelected = True #Set to zero to avoid a loop
                if M_n:
                    print("master selected")
                    DP.menuLevel = 1
                    DP.BMSSelected = CM.MM.BMS_Master
                    DP.infoSelected = True #Set to zero to avoid a loop
                if S1_n:
                    DP.menuLevel = 1
                    DP.BMSSelected = CM.MM.BMS_Slave1
                    DP.infoSelected = True #Set to zero to avoid a loop
                if S2_n:
                    DP.menuLevel = 1
                    DP.BMSSelected = CM.MM.BMS_Slave2
                    DP.infoSelected = True #Set to zero to avoid a loop 
            elif DP.menuLevel == 1:
                DP.tilesSelected = False
                batteryTileStyle = {'display':'none'}
       
                backTileStyle =  {'display':'block'}
                

                if DP.infoSelected :
                    
                    batteryinfoStyle = {'display':'block'}
                    if back_n:
                        DP.infoSelected = False
   


                        DP.menuLevel = 0
                        batteryinfoStyle = {'display':'none'}
                        print("Back pressed")

                    elif cell_info_n:
                        DP.cellInfoSelected = True
                        #DP.menuLevel = DP.menuLevel + 1
                        print("cell info selected")
                    elif details_n:
                        DP.detailsSelected = True
                        #DP.menuLevel = DP.menuLevel + 1
                    elif active_alarms_n:
                        print('activ alarms set')
                        print(DP.BMSSelected.BMSName)
                        DP.activeAlarmsSelected = True
                        DP.menuLevel = 2
                    elif alarms_history_n:
                        DP.alarmsHistorySelected = True
                        DP.menuLevel = DP.menuLevel + 1
                    elif IO_cond_n:
                        DP.IOSelected = True
                        DP.menuLevel = 2
                        print("io pressed")
                    else:
                        pass
            elif DP.menuLevel == 2:
                backTileStyle =  {'display':'block'}
                batteryTileStyle = {'display':'none'}
                batteryinfoStyle = {'display':'none'}

                if DP.alarmsHistorySelected:
                    alarmHistoryStyle = {'display':'block'}
                elif DP.activeAlarmsSelected:
                    activeAlarmStyle = {'display':'block'}
                elif DP.IOSelected:
                    IOConditionsStyle =  {'display':'block'}
                if back_n:

                    DP.detailsSelected = False
                    DP.activeAlarmsSelected = False
                    DP.alarmsHistorySelected = False
                    DP.batteryHistorySelected = False
                    DP.IOSelected = False
                    DP.cellInfoSelected = False
                    alarmHistoryStyle = {'display':'none'}
                    activeAlarmStyle = {'display':'none'} 
                    IOConditionsStyle =  {'display':'none'}
                    DP.menuLevel = 1


            else:
                pass
          
        else: 
            loadingScreenStyle = {'display':'block', 'width':'100%'}
            print("Start reading timer")
            CM.startCANBusRead()

        
    else:
        loadingScreenStyle = {'display':'block', 'width':'100%'}
        connectStringTemp = ""
        if CM.startCANDevice():
            print("CANBus started successfully")
            connectStringTemp = "CANBus connection successful ! "
        else:
            print("still trying to connect")
            connectStringTemp = "Trying to connect to CANBus \n Make sure the device is connected properly."
        print("____________####_____still trying to connect____######__________")

    
    return [
        #loading screen
        html.Div("VOYAGE Charters Battery Monitor",className='top_banner'),
        html.Div(className = "back_tile_parent ",style = backTileStyle,  children = html.Div(className = "back_tile ",children = [dbc.Button("Back", color="secondary", className="me-1 back-button",id='back_btn')])),
       
        html.Div(style=loadingScreenStyle ,children=[html.Div(className="loading_screen",children=[html.Img(src="/assets/images/voyage-logo-color-dark.png",className='loading_img')])]),
        load_tiles(batteryTileStyle, DP.tilesSelected),
        html.Div(className="info_row_parent",style=batteryinfoStyle,children=create_battery_info(DP.BMSSelected)),
        html.Div(className="info_row_parent", style=activeAlarmStyle,children=create_active_alarms(DP.BMSSelected)),
        html.Div(className="info_row_parent",style=alarmHistoryStyle,children=create_alarm_history(DP.BMSSelected)),
        html.Div(className="info_row_parent",style=IOConditionsStyle,children=create_io_conditions(DP.BMSSelected)),
        

        html.Div(style = resetTileStyle,  children = html.Div(className = "reset_tile ",children = [dbc.Button("Reset BMS", color="warning", className="me-1",id='bms_reset',n_clicks=0)])),
        #html.Div(className='reset_tile',style=resetStyle)
    
    ]
#def render_main(n,n_master_combined,n_master,n_slave1,n_slave2):
    
#reset all bmss
@app.callback(
    Output('test_text','children'),
    Input('bms_reset','n_clicks'),
    prevent_initial_call=True,
    )
    

def call_bms_reset(n_clicks):
    #print("reset button pressed")
    if n_clicks:
        print("reset button pressed")
        CM.BMSResetAll()




#run if this is the main script being run
if __name__ == '__main__':

    app.run_server(host= '0.0.0.0',debug=False)

    # while not CM.isConnected:
    #     connectStringTemp = ""
    #     if CM.startCANDevice():
    #         print("CANBus started successfully")
    #         connectStringTemp = "CANBus connection successful ! "
    #     else:
    #         # connectAttempt = connectAttempt + 1
    #         # connectStringTemp = connectString
    #         # for x in range(0,connectAttempt):
    #         #     connectStringTemp = connectStringTemp + "."
    #         # if connectAttempt == 10:
    #         #     connectAttempt = 1
    #         # print(connectStringTemp)
    #         print("still trying to connect")
    #         connectStringTemp = "Trying to connect to CANBus \n Make sure the device is connected properly."
    #         #print(connectString)
    #     time.sleep(1)
    #     #print("____________####_____still trying to connect____######__________")       
    # while not CM.isRunning:
    #     print("Start reading timer")
    #     CM.startCANBusRead()
    #     time.sleep(1)

    #Start flask app

    
    
    #CM.startCAN()
    ## Reading messages...
    # have some sort of indicatio that the background tasks are indeed running
    #
