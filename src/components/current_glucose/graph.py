from dash import Dash, dcc, html
from src.const import *
from . import ids
from dash.dependencies import Input, Output
from datetime import datetime, timedelta
import plotly.express as px
import pandas as pd


def render(app: Dash) -> html.Div:
    
    @app.callback(
        Output(ids.GLUCOSE_GRAPH, 'children'),
        Input(ids.DATA_STORAGE, 'data'),
        Input(ids.GLUCOSE_HISTORY_RADIOS, 'value'),
        Input(ids.UPDATE_BUTTON, 'n_clicks'))
    def update_graph(data: dict, value: int, _) -> dcc.Graph:
        if data is None or not data:
            return html.Div([dcc.Graph(figure=px.scatter(template="plotly_dark"))], className='container-bigger')
            
        df = pd.DataFrame(data)
        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df[df['datetime'] > datetime.now() - timedelta(hours=value)]

        marker_size = 10
        fig = px.scatter(df, x="datetime", y="mmol_l", template="plotly_dark", color="range",
                         color_discrete_map=color_map, labels={
                             "datetime": "Time",
                             "mmol_l": "mmol/L",
                         }, hover_data={"mmol_l": ":.1f", "range": False, "datetime": False})
        fig.update_traces(marker={'size': marker_size})

        fig.data = fig.data[::-1]
        fig.update_layout(showlegend=False)
        fig.update_layout(height=600)
        fig.update_traces(hovertemplate='%{y:.1f}<extra></extra>',)
        fig.update_layout(hovermode="x")
        fig.add_hline(y=RANGE[0], line_width=1, line_color=color_map['high'])
        fig.add_hline(y=RANGE[1], line_width=1, line_color=color_map['low'])

        return dcc.Graph(figure=fig)

    return html.Div(className='container-bigger', id=ids.GLUCOSE_GRAPH)

