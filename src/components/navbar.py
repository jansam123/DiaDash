from dash import Dash, html
import dash_bootstrap_components as dbc
from .current_glucose import ids
from src.const import *


def render(app: Dash) -> html.Div:

    nav_content = [
        # dbc.NavItem(dbc.NavLink("Current Glucose", href="/", active='exact')),
        dbc.NavItem(dbc.NavLink(html.I(className="fa-solid fa-house"), href="/", active='exact')),
        dbc.NavItem(dbc.NavLink(html.I(className="fa-solid fa-table"), href="/table", active='exact')),
        dbc.NavItem(dbc.NavLink(html.I(className="fa-solid fa-chart-line"), href="/statistics", active='exact')),
        dbc.NavItem(dbc.NavLink(html.I(className="fa-solid fa-upload"), href="/upload", active='exact')),
    ]

    navbar = dbc.Nav(
        nav_content,
        pills=True,
        vertical=True,
        class_name='mb-3 nav-pills',
    )
    SIDEBAR_STYLE = {
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "3rem",
    }
    return html.Div(children=[navbar], className='bg-light', style=SIDEBAR_STYLE)
