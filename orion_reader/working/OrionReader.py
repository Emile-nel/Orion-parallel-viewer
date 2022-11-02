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

OrionPCAN = None
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

IS_WINDOWS = platform.system() == 'Windows'
# if IS_WINDOWS:
#     OrionPCAN = TimerRead()
#OrionPCAN.GetDataInt

cell_id = 0

def create_battery_card(batteryName,voltage,current,power,soc,isFault,batteryId):
    if power < 1000 :
        power_string = '{power:.1f} W'.format(power=power)
    else:
        power_string = '{power:.1f} kw'.format(power=power/1000)

    if -1 < current < 1:#in idle
        soc_string = '{soc} idle'.format(soc=soc)
    if current >= 1: #Charging
        soc_string = '{soc} charging'.format(soc=soc)
    if current <= -1: # Discharging
        soc_string = '{soc} discharging'.format(soc=soc)


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
                                html.H5("FAULT", className="p-2", style={ "height":"50%", "color" : "red"})                        
                            ]),
            ],className="battery-tile align-items-center text-start ",
        )
    ], className="justify-content-center"
),id=batteryId,n_clicks=0,style={"width":"85%","max-width":"800px","min-width":"700px"})


app.layout = html.Div([
    #main div
    html.Div(
        
        className="main-body",
        children=[
            html.H5("Summer Breez Battery Monitor"),
            create_battery_card('Orion Master Combined',156.22432,50.2,500,53,False,'master_combined'),
            create_battery_card('Orion Master',156.22432,50.2,500,53,False,'master'),
            create_battery_card('Orion Slave1',156.22432,0.12,5000,53,False,'slave1'),
            create_battery_card('Orion Slave2',156.22432,-50.2,500,53,False,'slave2'),
            html.Div(id="masterCombinedSelected",children="",),
            html.Div(id="masterSelected",children="",),
            html.Div(id="slave1Selected",children="",),
            html.Div(id="slave2Selected",children="",),

    ],
    ),
    html.H6("This is just a Teeeessstt"),
    html.Button('Start/Stop',id="ss",n_clicks=0),
    html.Div(id="state_ind", children="should be stopped"),
    html.Div(id='live-update-text'),
    dcc.Interval(
        id = 'interval-component',
        interval=3*1000, # in milliseconds
        n_intervals=0
    )

])

@app.callback(Output('live-update-text', 'children'),
              Input('interval-component', 'n_intervals'))
def update_metrics(n):

    return "testing phase"
    
    # msg_list = []
    # for msg in OrionPCAN.MM.CANMsgs_Master:
    #     msg_list.append(html.Div([
    #         html.Span("%s  with ID : %d has a value of : "%(msg.name,msg.id)),
    #         html.Span(msg.timeStamp)
    #         ]))
        
    # test_value = str(OrionPCAN.MM.CANMsgs_Master[0].value)
    # #test_value  = n

    # style = {'padding': '5px', 'fontSize': '16px'}
    # if OrionPCAN.get_running_state:
    #     #return html.Span(test_value,style=style)
    #     return msg_list
    # else:
    #     return html.Span('The bus is not running anymore bru:',style=style)

@app.callback(
    Output("masterCombinedSelected","children"),
    Input("master_combined","n_clicks"),
)
def update_state(n_clicks):
    return "Master-Combined selected {n} times".format(n=n_clicks)

@app.callback(
    Output("masterSelected","children"),
    Input("master","n_clicks"),
)
def update_state(n_clicks):
    return "Master selected {n} times".format(n=n_clicks)

@app.callback(
    Output("slave1Selected","children"),
    Input("slave1","n_clicks"),
)
def update_state(n_clicks):
    return "Slave 1 selected {n} times".format(n=n_clicks)

@app.callback(
    Output("slave2Selected","children"),
    Input("slave2","n_clicks"),
)
def update_state(n_clicks):
    return "Slave 2 selected {n} times".format(n=n_clicks)

def update_state(n_clicks):
    return "testing phase"
    # if (n_clicks%2) != 0:
    #     OrionPCAN.start_reading()
    #     print('started_probably')
    # else:
    #     OrionPCAN.stop_reading
    #     print("stopped .... probably")

    # if OrionPCAN.get_running_state:
    #     return "The bus seems to be running"
    # else:
    #     return "The bus is not running anymore bruh"




#run if this is the main script being run
if __name__ == '__main__':
    if IS_WINDOWS:
        ## Starts the program
        #TimerRead()
        print("timerread")
        
        #Run windows with PCAN device reader
    else:
        #Run Raspberry pi setup with socketCAN
        print("gogo raspberry")
    # have some sort of indicatio that the background tasks are indeed running
    app.run_server(debug=False)
