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

battery_card = dbc.Container(
    [
        html.Div(

        ),
        dbc.Row(
            
            [
                dbc.Col(className="col-md-2 ",
                children=[html.Img(src="/assets/images/batery_icon.png")]),
                dbc.Col(className="col-md-10",
                children=[
                    html.Div("Orion BMS - Master"),
                    dbc.Row(
                        children=[
                        dbc.Col(className="col-md-3",children=[html.Div("146.5 V")]),
                        dbc.Col(className="col-md-3",children=[html.Div("56 A")]),
                        dbc.Col(className="col-md-3",children=[html.Div("15.4 kw")]),]
                    )
                ]),

            ],className="battery-tile align-items-center text-start "
        )
    ], className="justify-content-center"
)

app.layout = html.Div([
    #main div
    html.Div(
        className="main-body",
        children=[
            battery_card,
            battery_card,
            battery_card,

    ],
    ),
    html.H6("This is just a Teeeessstt"),
    html.Button('Start/Stop',id="ss",n_clicks=0),
    html.Div(id="state_ind", children="should be stopped"),
    html.Div(id='live-update-text'),
    dcc.Interval(
        id = 'interval-component',
        interval=1*1000, # in milliseconds
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
    Output("state_ind","children"),
    Input("ss","n_clicks"),
    
)
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
    app.run_server(debug=False)
    if IS_WINDOWS:
        ## Starts the program
        #TimerRead()
        print("timerread")
        
        #Run windows with PCAN device reader
    else:
        #Run Raspberry pi setup with socketCAN
        print("gogo raspberry")
    # have some sort of indicatio that the background tasks are indeed running



