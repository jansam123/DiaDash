import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash import Dash, html
from numpy import argmax

def render(labels: list[str], id: str, app: Dash) -> html.Div:
    element_ids = [f'changing-dropdown-{label}' for label in labels]
    @app.callback(
        Output(id, 'label'),
        [Input(element_id, 'n_clicks_timestamp') for element_id in element_ids])
    def dropdown_change_name(*args):
        return labels[argmax(args)]

    return html.Div([dbc.DropdownMenu(
        label=labels[0],
        id=id,
        menu_variant="dark",
        children=[dbc.DropdownMenuItem(
            label, n_clicks=0, id=element_id, n_clicks_timestamp=0) for label, element_id in zip(labels, element_ids)],
    )])
