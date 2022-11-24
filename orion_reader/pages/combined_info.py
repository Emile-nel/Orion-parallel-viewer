from PCANOrionReader import *
import dash
from dash import dcc, ctx
import dash_html_components as html
import dash_bootstrap_components as dbc





#dash.register_page(__name__)

def create_combined_info(BMS : CombinedBMSUnit):

    
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
            statusString = "RELAY OPEN"
            statusStyle = { "height":"50%", "color" : "red"}          
        else:
            statusString = "OK"
            statusStyle = { "height":"50%", "color" : "green"}
    else:
        statusString = "CONN. ERROR"
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
                        dbc.Col("{}".format(statusString),className="col-md-8 info_value ",style={'max-width':'150px'}),
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
        html.Div(
            id = "details_btn",
            style = {'width':'100%'},
            n_clicks = 0,
            children= [
                dbc.Row(
                    className="info_row row justify-content-between",
                    children=[
                        dbc.Col("Details", className="col-md-8 info_name"),
                        dbc.Col(className="col-md-4 info_name", 
                        children = [
                            dbc.Row(
                            className="row justify-content-end",
                            children=[
                                dbc.Col(">",className="col info_value"),
                            ]
                        )
                        ]),
                    ]
                ),
            ]),
            #lowest Cell [cell : voltage]
            #Highest Cell [cell : voltage]
            #min Temp [cell : temp]
            #max temp [cell : temp]
            #Battery Modules 
            #Installed capacity
            #Balancing ? 
        #Active Alarms
        html.Div(
            id = "active_alarms_btn",
            style = {'width':'100%'},
            n_clicks = 0,
            children= [
                dbc.Row(
                    
                    className="info_row row justify-content-between",
                    children=[
                        dbc.Col("Active Alarms", className="col-md-8 info_name"),
                        dbc.Col(className="col-md-4 info_name", 
                        children = [
                            dbc.Row(
                            className="row justify-content-end",
                            children=[
                                dbc.Col(">",className="col info_value"),
                            ]
                        )
                        ]),
                    ]
                ),
            ]),
        #Alarm history
        html.Div(
            id = "alarms_history_btn",
            style = {'width':'100%'},
            n_clicks = 0,
            children= [
                dbc.Row(
                    
                    className="info_row row justify-content-between",
                    children=[
                        dbc.Col("Alarms History", className="col-md-8 info_name"),
                        dbc.Col(className="col-md-4 info_name", 
                        children = [
                            dbc.Row(
                            className="row justify-content-end",
                            children=[
                                dbc.Col(">",className="col info_value"),
                            ]
                        )
                        ]),
                    ]
                ),
            ]),
        #Battery History
        html.Div(
            id = "battery_history_btn",
            style = {'width':'100%'},
            n_clicks = 0,
            children= [
                dbc.Row(
                    
                    className="info_row row justify-content-between",
                    children=[
                        dbc.Col("Battery History", className="col-md-8 info_name"),
                        dbc.Col(className="col-md-4 info_name", 
                        children = [
                            dbc.Row(
                            className="row justify-content-end",
                            children=[
                                dbc.Col(">",className="col info_value"),
                            ]
                        )
                        ]),
                    ]
                ),
            ]),
        
        #IO
        html.Div(
            id = "IO_cond_btn",
            style = {'width':'100%'},
            n_clicks = 0,
            children= [
                dbc.Row(
                    id = "IO_btn",
                    className="info_row row justify-content-between",
                    children=[
                        dbc.Col("IO Conditions", className="col-md-8 info_name"),
                        dbc.Col(className="col-md-4 info_name", 
                        children = [
                            dbc.Row(
                            className="row justify-content-end",
                            children=[
                                dbc.Col(">",className="col info_value"),
                            ]
                        )
                        ]),
                    ]
                ),
            ]),
        #Cell Info
        html.Div(
            id = "cell_info_btn",
            style = {'width':'100%'},
            n_clicks = 0,
            children= [
                dbc.Row(
                    
                    className="info_row row justify-content-between",
                    children=[
                        
                            dbc.Col("Cell Info", className="col-md-6 info_name"),
                            dbc.Col(className="col-md-4 info_name", 
                            children = [
                                dbc.Row(
                                className="row justify-content-end",
                                children=[
                                    dbc.Col(">",className="col info_value"),
                                ]
                            )
                            ]),
                        

                    ]
                ),
            ]
        )

        


        
        

        
    ]
        
    )
        
   