from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from datetime import date, datetime, timedelta
from . import ids
from dash.dependencies import Input, Output


def render(app: Dash) -> html.Div:

    date_range_buttons = html.Div(
        [
            dbc.RadioItems(
                id=ids.TABLE_FAST_RANGE,
                className="btn-group",
                inputClassName="btn-check",
                labelClassName="btn btn-outline-primary",
                options=[
                    {"label": "120d", "value": 120},
                    {"label": "90d", "value": 90},
                    {"label": "30d", "value": 30},
                    {"label": "14d", "value": 14},
                    {"label": "Manual", "value": -1},
                ],
                value=120,
            ),
            html.Div(id="output"),
        ],
        className="radio-group mt-3",
    )

    @app.callback(
        Output(ids.DATE_PICKER_DIV, 'children'),
        Input(ids.TABLE_FAST_RANGE, 'value'),
    )
    def fast_date_update(value) -> html.Div:
        disabled = True if value != -1 else False
        start_date = datetime.today() - timedelta(days=value if value != -1 else 120)
        end_date = datetime.today()

        return html.Div([
            dcc.DatePickerRange(
                id=ids.DATE_PICKER,
                min_date_allowed=date(2000, 11, 9),
                max_date_allowed=datetime.today(),
                initial_visible_month=datetime.today(),
                start_date=start_date,
                end_date=end_date,
                display_format='DD.MM.YYYY',
                disabled=disabled
            ),
        ], className="dash-bootstrap ms-4")

    return html.Div([
        dbc.Row([
            dbc.Col([html.Div([html.Div([
                dcc.DatePickerRange(
                    id=ids.DATE_PICKER,
                    min_date_allowed=date(2000, 11, 9),
                    max_date_allowed=datetime.today(),
                    initial_visible_month=datetime.today(),
                    start_date=datetime.today() - timedelta(days=120),
                    end_date=datetime.today(),
                    display_format='DD.MM.YYYY',
                    disabled=False
                ),
            ], className="dash-bootstrap ms-4")], id=ids.DATE_PICKER_DIV)], width=8),
            dbc.Col([
                html.Div([
                    html.Button('Update', id=ids.UPDATE_TABLE, className="btn btn-primary"),
                ]), ], width=3),
        ]),
        date_range_buttons,
    ], className='mb-3')
