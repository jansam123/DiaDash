from dash import Dash, html
from . import date_range, glucose_data_storage, trend_plot, insulin_data_storage, insulin_violin, TIR, mode_switcher, histogram, pie_TIR, heatmap, metrics
import dash_bootstrap_components as dbc
from . import ids
from dash.dependencies import Input, Output


def create_layout(app: Dash) -> html.Div:
    @app.callback(
        Output(ids.PLOT_CONTAINER, 'className'),
        Input(ids.THEME_TOGGLE_SWITCH, 'value'))
    def change_bg_color(value: bool):
        if value:
            return ''
        else:
            return 'bg-white'

    return html.Div([
        glucose_data_storage.render(app),
        insulin_data_storage.render(app),
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div([pie_TIR.render(app)]),
                ], width=3),
                dbc.Col([
                    html.Div([trend_plot.render(app)]),
                ], width=5),
                dbc.Col([
                    html.Div([histogram.render(app)]),
                ], width=4),
            ], className='mt-4'),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Div([mode_switcher.render(app)]),
                        html.Div([date_range.render(app)]),
                    ]),
                ], width=1),
                dbc.Col([metrics.render(app)], width=10),
                # dbc.Col([html.Div()], width=1),
            ], className='mt-4 mb-2'),
            dbc.Row([
                dbc.Col([
                    html.Div([heatmap.render(app)]),
                ], width=5),
                dbc.Col([
                    html.Div([insulin_violin.render(app)]),
                ], width=4),
                dbc.Col([
                    html.Div([TIR.render(app)]),
                ], width=3),
            ]),
        ])
    ], id=ids.PLOT_CONTAINER)
