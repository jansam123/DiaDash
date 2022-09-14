from dash import Dash, html
import dash_bootstrap_components as dbc
from src.const import *
from . import ids
from dash.dependencies import Input, Output
from datetime import datetime
import pandas as pd


def update_buttons_panel(app:Dash) -> html.Div:
    time_range_buttons = html.Div(
        [
            dbc.RadioItems(
                id=ids.GLUCOSE_HISTORY_RADIOS,
                className="btn-group",
                inputClassName="btn-check",
                labelClassName="btn btn-outline-primary",
                labelCheckedClassName="active",
                options=[
                    {"label": "24h", "value": 24},
                    {"label": "12h", "value": 12},
                    {"label": "6h", "value": 6},
                    {"label": "3h", "value": 3},
                ],
                value=6,
            ),
            html.Div(id="output"),
        ],
        className="radio-group",
    )
    
    return html.Div([
        html.Div([
                    html.Div([
                        html.Button('Update', id=ids.UPDATE_BUTTON, n_clicks=0, className="btn btn-primary"),
                    ]),
                    html.Hr(),
                    time_range_buttons,
                    ], className="card mb-3 bg-body text-white card-body")],
        style={'width': '30%', 'display': 'inline-block'},)
    
def current_glucose_panel(app:Dash) -> html.Div:
    @app.callback(
    Output(ids.CURRENT_GLUCOSE_CONTAINER, 'children'),
    Input(ids.DATA_STORAGE, 'data'),
    Input(ids.MINUTE_INTERVAL, 'n_intervals'),)
    def update_last_reading(data: dict, n_intervals: int) -> html.Div:
        if data is None or not data:
            return html.Div(children=[
                html.H1(children='---'),
                html.H5(children='---'), ],
                className=f'card text-white bg-danger mb-3')

        df = pd.DataFrame(data)
        last_reading = df[df["datetime"] == df["datetime"].max()]
        last_value = last_reading["mmol_l"].values[0]
        last_arrow = last_reading["trend_arrow"].values[0]

        if last_value > RANGE[0]:
            color = 'warning'
        elif last_value < RANGE[1]:
            color = 'danger'
        else:
            color = 'success'

        last_datetime = f'{last_reading["time"].values[0][:-3]}  {last_reading["day"].values[0].replace("-", ".")}'
        time_delta = datetime.now() - pd.to_datetime(last_reading["datetime"].values[0])
        time_delta = int(round(time_delta.seconds/60, 0))
        if time_delta > 120:
            time_delta = '---'

        return html.Div(children=[
            html.H1(children=str(last_value)+last_arrow),
            html.H4(children=f'{time_delta} min'),
            html.H5(children=last_datetime), ],
            className=f'card text-white bg-{color} mb-3 card-body')
        
    return html.Div(id=ids.CURRENT_GLUCOSE_CONTAINER, style={'width': '25%', 'display': 'inline-block'}, )



def render(app: Dash) -> html.Div:
    
    return html.Div([
        current_glucose_panel(app),
        update_buttons_panel(app),
    ], className="container")
