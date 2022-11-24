from PCANOrionReader import *
import dash
from dash import dcc, ctx
import dash_html_components as html
import dash_bootstrap_components as dbc









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
