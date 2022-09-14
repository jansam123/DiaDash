from dash import Dash, html
import dash
from . import navbar



def create_layout(app: Dash) -> html.Div:
    CONTENT_STYLE = {
        "margin-left": "5rem",
        "margin-right": "2rem",
        # "padding": "2rem 1rem",
    }
    return html.Div([
        navbar.render(app),
        html.Div([dash.page_container], style=CONTENT_STYLE)
        ])

