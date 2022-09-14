from dash import Dash, html, dcc
from . import ids
from src import const 
from src.data.loader import get_glucose_data
from dash.dependencies import Input, Output, State
from datetime import datetime


def render(app: Dash) -> html.Div:

    @app.callback(
        Output(ids.GLUCOSE_DATA_STORAGE, 'data'),
        State(ids.STAT_DATE_PICKER, 'start_date'),
        State(ids.STAT_DATE_PICKER, 'end_date'),
        Input(ids.UPDATE_STATS, 'n_clicks'),)
    def load_data(start, end, n_clicks) -> dict:
        df = get_glucose_data(datetime.fromisoformat(end), datetime.fromisoformat(start),
                              folder=const.DATA_FOLDER, cols=['mmol_l', 'time', 'day'])
        if df is None:
            return {}
        # df["range"] = df["mmol_l"].apply(lambda x: 'high' if x > RANGE[0] else 'low' if x < RANGE[1] else 'ok')
        out = df.to_dict('records')
        return out

    return html.Div(children=[dcc.Store(storage_type='memory', id=ids.GLUCOSE_DATA_STORAGE)])
