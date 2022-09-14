from dash import Dash, html
import dash_bootstrap_components as dbc

from . import ids
from src import const
from src.data.loader import get_glucose_data
from dash.dependencies import Input, Output
from datetime import datetime, timedelta


def render(app: Dash) -> html.Div:
    @app.callback(
        Output(ids.HIGH_TIR, 'value'),
        Output(ids.OK_TIR, 'value'),
        Output(ids.LOW_TIR, 'value'),
        Output(ids.HIGH_TIR, 'label'),
        Output(ids.OK_TIR, 'label'),
        Output(ids.LOW_TIR, 'label'),
        Input(ids.UPDATE_GRAPH_BUTTON, 'n_clicks'),)
    def get_TIR_progress(n_clicks):
        df = get_glucose_data(datetime.now(), datetime.now() - timedelta(days=1), folder=const.DATA_FOLDER)
        if df is None:
            return 0, 0, 0, '---', '---', '---'
        above = df.query('mmol_l > @const.RANGE[0]')['mmol_l'].count()
        below = df.query('mmol_l < @const.RANGE[1]')['mmol_l'].count()
        total = df['mmol_l'].count()
        above /= total
        below /= total
        above = round(above * 100, 1)
        below = round(below * 100, 1)
        inside = round(100 - above - below, 1)
        inside_label = f'{inside}%'
        below_label = f'{below}%'
        above_label = f'{above}%'
        return above, inside, below, above_label, inside_label, below_label

    TIR_progress = dbc.Progress(
        [
            dbc.Progress(color=const.color_map['low'], bar=True, id=ids.LOW_TIR),
            dbc.Progress(color=const.color_map['ok'], bar=True, id=ids.OK_TIR),
            dbc.Progress(color=const.color_map['high'], bar=True, id=ids.HIGH_TIR),
        ]
    )

    return html.Div([
        html.Div([TIR_progress]),
    ], className='container')
