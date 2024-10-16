from dash import Dash, dcc, html
from src import const
from . import ids
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
from . import figure_theme
import plotly.io as pio


def render(app: Dash) -> html.Div:

    @app.callback(
        Output(ids.TIR_GRAPH, 'children'),
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

        df = df[['mmol_l', 'time']]

        df['time'] = pd.to_datetime(df['time'], format='%H:%M:%S')
        df['hour'] = df['time'].dt.hour + df['time'].dt.minute / 60 + df['time'].dt.second / 3600
        df['hour'] = df['hour'].astype(int)
        bins = [0, 3.9, 10, 25]
        df['mmol_l'] = pd.cut(df['mmol_l'], bins=bins, labels=['low', 'ok', 'high'])
        df['hour'] = pd.cut(df['hour'], bins=[0, 8, 12, 18, 24], labels=['morning', 'lunch', 'evening', 'night'])
        total = df.groupby('hour', observed=True).count()
        
        figs = []
        for rag in ['low', 'ok', 'high']:
            count = df.query('mmol_l == @rag').groupby('hour', observed=True).count()
            count /= total/100
            figs += [go.Bar(x=count.index, y=count['mmol_l'], name=rag, marker_color=const.color_map[rag], text=count['mmol_l'],
                             textposition='auto')]

        fig = go.Figure(data=figs)
        fig.update_layout(title='Daily TIR')
        fig.update_traces(texttemplate='%{text:.1f}')
        fig.update_traces(hovertemplate='%{y:.1f}<extra></extra>',)
        fig.update_layout(hovermode="x")
        fig.update_layout(barmode='stack')
        fig.update_layout(height=400)
        fig.update_layout(showlegend=False)

        return html.Div([dcc.Graph(figure=fig)])

    return html.Div(id=ids.TIR_GRAPH)
