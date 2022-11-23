## Needed Imports
from ast import Or
from distutils.log import debug

from PCANBasic import *

from PCANOrionReader import *
import dash
from dash import Dash, html, dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc




OrionPCAN = None
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP],  use_pages=True)

IS_WINDOWS = platform.system() == 'Windows'



global connectAttempt
connectAttempt = 1
connectString = "Still trying to connect. Make sure the device is connected"

class displayParameters():

    masterCombinedSelected = False
    masterSelected = False
    slave1Selected = False
    slave2Selected = False
    slave3Selected = False

#OrionPCAN.GetDataInt

DP = displayParameters()

cell_id = 0


    

app.layout = (html.Div(children=[
    #main div
 
    # html.Div(   
    #     id = 'main_display', 
    #     className="main-body",

    # ),
    html.H1('Multi-page app with Dash Pages'),

    html.Div(
        [
            html.Div(
                dcc.Link(
                    f"{page['name']} - {page['path']}", href=page["relative_path"]
                )
            )
            for page in dash.page_registry.values()
        ]
    ),
    dash.page_container

    # dcc.Interval(
    #     id = 'interval-component',
    #     interval=3*1000, # in milliseconds
    #     #n_intervals=0
    # ),
    # html.Div(   
    #     id = 'battery_info_page', 
        
    # ),

    

    
    


]))



    
    



#run if this is the main script being run
if __name__ == '__main__':
    #Start flask app
    app.run_server(debug=False)
    #CM.startCAN()
    ## Reading messages...
    # have some sort of indicatio that the background tasks are indeed running
    #
