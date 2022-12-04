from PCANOrionReader import *
import dash
from dash import dcc, ctx
import dash_html_components as html
import dash_bootstrap_components as dbc



def create_active_alarms(BMS:BMSUnit):
    activeAlarmList = BMS.get_active_alarms()
    #print(activeAlarmList)
    rowList =[
        #add header
        dbc.Row(
                className="info_row row justify-content-between",
                children=[
                    dbc.Col("Error Description", className="col-md-8 info_name"),
                    dbc.Col("Condition",className="col-md-4 info_name", style={"text-align": "center"}),
                ]
                ),
    ]
    
    for alarm in activeAlarmList:
        #print(alarm)

        alarmRow =  dbc.Row(
                        className="info_row row justify-content-between",
                        children=[
                            dbc.Col("{}".format(alarm[0]), className="col-md-8 info_name"),
                            dbc.Col("{}".format(alarm[1]),className="col-md-4 info_name", style={"text-align": "center"}),
                        ]
                )
        rowList.append(alarmRow)
    return rowList
            