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
        Output(ids.TOTAL_TIR_GRAPH, 'children'),
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

        bins = [0, 3.9, 10, 25]
        df['mmol_l'] = pd.cut(df['mmol_l'], bins=bins, labels=['low', 'ok', 'high'])
        percentage_ok = df['mmol_l'].value_counts(normalize=True)['ok']*100

        fig = go.Figure(data=[go.Pie(labels=df['mmol_l'].value_counts().index,
                                     values=df['mmol_l'].value_counts().values,
                                     hole=0.5)])
        fig.update_traces(marker=dict(colors=[const.color_map['ok'], const.color_map['high'],
                                              const.color_map['low']],
                                      line=dict(color='#000000' if value else '#FFFFFF',
                                                width=2)),
                          textfont_size=10)
        fig.add_annotation(text=f'{percentage_ok:.1f}%', x=0.5, y=0.5, showarrow=False, font_size=35)

        fig.update_layout(title='Total TIR')
        fig.update_layout(height=300)
        fig.update_layout(showlegend=False)

        return html.Div([dcc.Graph(figure=fig)])

    return html.Div(id=ids.TOTAL_TIR_GRAPH)
