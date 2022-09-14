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

        df = df[['mmol_l']]
        df['range'] = pd.cut(df['mmol_l'], bins=[0, const.RANGE[1], const.RANGE[0], 25], labels=['low', 'ok', 'high'])

        fig = px.histogram(x=df['mmol_l'], nbins=50, color=df['range'], color_discrete_map=const.color_map)

        fig.update_layout(title='Glucose Histogram')
        
        fig.update_layout(xaxis_title='Glucose (mmol/L)')
        fig.update_layout(yaxis_title='Count')
        fig.update_layout(height=300)
        # fig.update_traces(opacity=0.75)
        fig.update_layout(showlegend=False)

        return html.Div([dcc.Graph(figure=fig)])

    return html.Div(id=ids.HIST_PLOT)
