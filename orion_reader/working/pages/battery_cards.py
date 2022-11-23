import dash
from dash import html, dcc
from .battery_info import batteryInfo

dash.register_page(
    __name__,
    name="Batter_Cards",
    
)

layout = html.Div(children=[
    html.H1(children='This is our Home page'),

    batteryInfo("This is a string")

])