from dash import Dash, html, dcc
from . import ids
from src.const import *
from src.data.loader import get_glucose_data
from dash.dependencies import Input, Output
from datetime import datetime, timedelta


def render(app: Dash) -> html.Div:

    @app.callback(
        Output(ids.DATA_STORAGE, 'data'),
        Input(ids.UPDATE_GRAPH_BUTTON, 'n_clicks'),
        Input(ids.AUTOUPDATE_INTERVAL, 'n_intervals'))
    def load_24h_data(n_clicks, n_intervals) -> dict:
        df = get_glucose_data(datetime.now(), datetime.now() - timedelta(days=1), folder=DATA_FOLDER)
        if df is None:
            return {}

        df["range"] = df["mmol_l"].apply(lambda x: 'high' if x > RANGE[0] else 'low' if x < RANGE[1] else 'ok')
        return df.to_dict()

    return html.Div(children=[dcc.Store(storage_type='local', id=ids.DATA_STORAGE)])
