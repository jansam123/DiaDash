from __future__ import annotations
from dash import Dash, dcc, html
from src import const
from . import ids
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from . import figure_theme
import plotly.io as pio
from .utils import split_into_periods
pio.templates.default = "my_cyborg"


def render(app: Dash) -> html.Div:

    @app.callback(
        Output(ids.HEATMAP_GRAPH, 'children'),
        Input(ids.GLUCOSE_DATA_STORAGE, 'data'),
        Input(ids.THEME_TOGGLE_SWITCH, 'value'))
    def update_graph(data: dict, value: bool) -> html.Div:
        if data is None or not data:
            return html.Div('Error: No data available.')
        if value:
            pio.templates.default = "my_cyborg"
        else:
            pio.templates.default = "white_cyborg"

        df = pd.DataFrame(data)
        df = df[['datetime', 'mmol_l']]
        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df.groupby(pd.Grouper(key='datetime', freq='1h')).mean()
        df = df.pivot_table(index=df.index.date, columns=df.index.hour, values='mmol_l')

        fig = px.imshow(df.T, color_continuous_scale='Turbo', color_continuous_midpoint=7)

        #set yaxis label
        fig.update_yaxes(title_text='Time', tickvals=list(range(0, 23, 2))) 
        fig.update_layout(height=400)
        
        fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)
        fig.update_layout(title='Glucose Patterns')
        return html.Div([dcc.Graph(figure=fig)])

    return html.Div(id=ids.HEATMAP_GRAPH)
