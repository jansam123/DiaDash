from dash import Dash, dcc, html
from src import const
from . import ids
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from . import figure_theme
import plotly.io as pio


def render(app: Dash) -> html.Div:

    @app.callback(
        Output(ids.HIST_PLOT, 'children'),
        Input(ids.INSULIN_DATA_STORAGE, 'data'),
        Input(ids.THEME_TOGGLE_SWITCH, 'value'))
    def update_graph(data: dict, value: bool) -> html.Div:
        if data is None or not data:
            return html.Div('Error: No data available.')
        if value:
            pio.templates.default = "my_cyborg"
        else:
            pio.templates.default = "white_cyborg"

        df = pd.DataFrame(data)[['day', 'value']]
        df = df.groupby('day').sum().reset_index()
        df['day'] = pd.to_datetime(df['day'], format='%d-%m-%Y')

        #create a scatter plots with date on x-axis and value on y-axis
        fig = px.scatter(df, x='day', y='value', trendline='lowess', title='Insulin Dosage per Day')
        # change color of the trendline
        fig.update_traces(line=dict(color='red', width=3))
        # change the size of the markers based on the len(df)
        if len(df) < 10:
            size=10
        elif len(df) < 20:
            size=9
        elif len(df) < 31:
            size=8
        elif len(df) < 95:
            size=7
        elif len(df) < 125:
            size=6
        fig.update_traces(marker=dict(size=size))
        
        fig.update_layout(height=400)
        fig.update_layout(xaxis_title='Day')
        fig.update_layout(yaxis_title='Insulin Dosage')
        fig.update_layout(title='Insulin Dosage per Day')
        
        


        return html.Div([dcc.Graph(figure=fig)])

    return html.Div(id=ids.HIST_PLOT)
