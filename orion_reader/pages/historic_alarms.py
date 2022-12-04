from PCANOrionReader import *
import dash
from dash import dcc, ctx
import dash_html_components as html
import dash_bootstrap_components as dbc



def create_alarm_history(BMS:BMSUnit):
    historicAlarms = BMS.get_alarm_history()
    #print(activeAlarmList)
    rowList =[
        #add header
        dbc.Row(
                className="info_row row justify-content-between",
                children=[
                    dbc.Col("Error Description", className="col-md-6 info_name"),
                    dbc.Col("Action",className="col-md-3 info_name", style={"text-align": "center"}),
                    dbc.Col("Date",className="col-md-3 info_name", style={"text-align": "center"}),
                ]
                ),
    ]
    
    
    for alarm in historicAlarms:
        #print(alarm)

        alarmRow =  dbc.Row(
                        className="info_row row justify-content-between",
                        children=[
                            dbc.Col("{}".format(alarm[1]), className="col-md-6 info_name"),
                            dbc.Col("{}".format(alarm[2]),className="col-md-2 info_name", style={"text-align": "end"}),
                            dbc.Col("{}".format(alarm[0]),className="col-md-4 info_name", style={"text-align": "end"}),
                        ]
                )
        rowList.append(alarmRow)
    return rowList
            