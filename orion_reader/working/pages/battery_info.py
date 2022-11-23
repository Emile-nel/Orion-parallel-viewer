import dash
from dash import html, dcc



def batteryInfo(BMS : str):
    return  html.Div(children=[
        html.H1(children='This is our Home page'),

        html.Div(children="The passed string is {}".format(BMS)),
    ])
# def layout(BMS : BMSUnit):
#     return html.Div(id = "battery_info_page", children=[html.Div("This is the Battery info page for {}".format(BMS.BMSName)) ])
        #State
        #Battery
        #State of Charge
        #Battery Temperature [highest]
        #Consumed amphours ? 
        #Details
            #lowest Cell [cell : voltage]
            #Highest Cell [cell : voltage]
            #min Temp [cell : temp]
            #max temp [cell : temp]
            #Battery Modules 
            #Installed capacity
            #Balancing ? 
        #Active Alarms
        #Alarm history
        #IO
        
        