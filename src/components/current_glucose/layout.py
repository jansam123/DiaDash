from dash import Dash, dcc, html

from . import TIR_bar, data_storage, ids, top_control_panel, graph

from src.const import *

def create_layout(app: Dash) -> html.Div:

    return html.Div(children=[
        data_storage.render(app),
        top_control_panel.render(app),
        graph.render(app),
        dcc.Interval(
            id=ids.AUTOUPDATE_INTERVAL,
            interval=GLUCOSE_RELOAD_INTERVAL*1000,  # in milliseconds
            n_intervals=0
        ),
        dcc.Interval(
            id=ids.MINUTE_INTERVAL,
            interval=60*1000,  # in milliseconds
            n_intervals=0
        ),
        html.Br(),
        TIR_bar.render(app),
    ])
