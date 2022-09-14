from dash import Dash, html
from . import table, date_picker, save_table, import_data
import dash_bootstrap_components as dbc


def create_layout(app: Dash) -> html.Div:
    return html.Div(children=[
        html.Div([
            dbc.Row([
                dbc.Col(html.Div([date_picker.render(app)], className=''), width=4),
                dbc.Col(html.Div([save_table.render(app)]), width=3),
                dbc.Col(html.Div([import_data.render(app)]), width=3),
            ])
        ]),
        table.render(app),
    ], className='container-bigger')
