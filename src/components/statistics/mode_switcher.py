from dash import Dash, html
import dash_bootstrap_components as dbc
from . import ids


def render(app: Dash) -> html.Div:
    return html.Div([
        html.I(className='fa-regular fa-sun', style={'display': 'inline-block'}),
        dbc.Switch(
            id=ids.THEME_TOGGLE_SWITCH,
            value=True,
            className='ms-2',
            style={'display': 'inline-block'}
        ),
        html.I(className='fa-regular fa-moon', style={'display': 'inline-block'}),
    ],className='mb-3')