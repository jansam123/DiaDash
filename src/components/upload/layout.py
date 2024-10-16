from dash import Dash, html
from . import upload_clarity, upload_glooko
import dash_bootstrap_components as dbc


def create_layout(app: Dash) -> html.Div:
    return html.Div(children=[
        html.Div([
            dbc.Row([
                dbc.Col(html.Div([upload_clarity.render(app)]), width=4),
                dbc.Col(html.Div([upload_glooko.render(app)]), width=4),
            ])
        ]),
    ], className='container-bigger')
