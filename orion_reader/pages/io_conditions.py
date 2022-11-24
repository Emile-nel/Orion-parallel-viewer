from PCANOrionReader import *
import dash
from dash import dcc, ctx
import dash_html_components as html
import dash_bootstrap_components as dbc



def create_io_conditions(BMS : BMSUnit):
    if BMS.allowCharge:
        allowChargeString = "Yes"
    else:
        allowChargeString ="No"
    if BMS.allowDischarge:
        allowDischargeString = "Yes"
    else:
        allowDischargeString ="No"
    if BMS.relayState:
        relayStateString = "Closed"
    else:
        relayStateString ="Open"

    return [
        dbc.Row(
                        className="info_row row justify-content-between",
                        children=[
                            dbc.Col("Relay State", className="col-md-8 info_name"),
                            dbc.Col("{}".format(relayStateString),className="col-md-4 info_value"),
                        ]
                ),
        dbc.Row(
                        className="info_row row justify-content-between",
                        children=[
                            dbc.Col("Allow Charge", className="col-md-8 info_name"),
                            dbc.Col("{}".format(allowChargeString),className="col-md-4 info_value"),
                        ]
                ),
        dbc.Row(
                        className="info_row row justify-content-between",
                        children=[
                            dbc.Col("Allow Discharge", className="col-md-8 info_name"),
                            dbc.Col("{}".format(allowDischargeString),className="col-md-4 info_value"),
                        ]
                ),
    ]