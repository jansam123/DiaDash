from dash import Dash, dcc, html
from src import const
from . import ids
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from . import figure_theme
import plotly.io as pio
from .utils import split_into_periods


def render(app: Dash) -> html.Div:

    @app.callback(
        Output(ids.METRICS, 'children'),
        Input(ids.GLUCOSE_DATA_STORAGE, 'data'),
        Input(ids.INSULIN_DATA_STORAGE, 'data'),
        Input(ids.THEME_TOGGLE_SWITCH, 'value'))
    def update_graph(data: dict, insulin_data: dict, value: bool) -> html.Div:
        if data is None or not data:
            return html.Div('Error: No data available.')

        color = 'white' if value else 'rgb(46,63,92)'
        bg_color = '' if value else 'bg-white'

        df = pd.DataFrame(data)
        df = df[['mmol_l', ]]
        df['range'] = pd.cut(df['mmol_l'], bins=[0, const.RANGE[1], const.RANGE[0], 25], labels=['low', 'ok', 'high'])
        TIR = df['range'].value_counts(normalize=True)
        TIR = TIR.to_dict()
        average = df['mmol_l'].mean()

        in_df = pd.DataFrame(insulin_data)
        in_df = in_df[['value', 'time', 'day']]
        average_insulin_per_day = in_df.groupby('day')['value'].sum().mean()
        in_df['time'] = pd.to_datetime(in_df['time'], format='%H:%M:%S').dt.time
        period_df = split_into_periods(in_df, 'time')
        average_insulin_per_period = [per['value'].mean() for per in period_df]

        return html.Div([
            html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H5(f"{TIR['high']:.1%}", style={'color': const.color_map['high']}),
                            html.H2(f"{TIR['ok']:.1%}", style={'color': color}),
                            html.H5(f"{TIR['low']:.1%}", style={'color': const.color_map['low']}),
                        ], style={'text-align': 'center'}),
                    ]),
                    dbc.Col([
                        html.Div([
                            html.H5('Average Glucose', style={'color': color}),
                            html.H2(f'{average:.1f} mmol/L', style={'color': color})], style={'text-align': 'center'}),
                    ]),
                    dbc.Col([
                        html.Div([
                            html.H5('Average Insulin Dosage per Day', style={'color': color}),
                            html.H2(f'{average_insulin_per_day:.1f} IU', style={'color': color}),
                        ], style={'text-align': 'center'}),
                    ]),
                    dbc.Col([
                        html.Div([
                            *[html.Div([html.I(className=f'{per} me-3', style={'display': 'inline-block'}), html.H4(f'{avg:.1f} IU', style={'color': color, 'display': 'inline-block'})])
                              for avg, per in zip(average_insulin_per_period, ['fa-solid fa-mug-saucer', 'fa-regular fa-sun', 'fa-regular fa-moon'])],
                        ], style={'text-align': 'center'}),
                    ]),
                ]),
            ], className=f'card-body card-text'),
        ], className=f'card border-info mb-3 {bg_color}')

    return html.Div(id=ids.METRICS)
