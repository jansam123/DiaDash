from __future__ import annotations
from dash import Dash, dcc, html
from . import ids
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
from . import figure_theme
import plotly.io as pio
from .utils import split_into_periods
pio.templates.default = "my_cyborg"


def render(app: Dash) -> html.Div:

    @app.callback(
        Output(ids.INSULIN_VIOLIN_GRAPH, 'children'),
        Input(ids.INSULIN_DATA_STORAGE, 'data'),
        Input(ids.THEME_TOGGLE_SWITCH, 'value'))
    def update_graph(data: dict, value: bool) -> html.Div:
        if value:
            pio.templates.default = "my_cyborg"
            annotation_bg_color = "#000000"
        else:
            pio.templates.default = "white_cyborg"
            annotation_bg_color = "#ffffff"

        if data is None or not data:
            fig = go.Figure([go.Violin()])
            fig.update_layout(title='Insulin Violin Plot')
            fig.update_layout(height=300)
            return html.Div([dcc.Graph(figure=fig)])

        df = pd.DataFrame(data)
        df = df[['value', 'time']]

        fig = go.Figure()
        df['time'] = pd.to_datetime(df['time']).dt.time
        period_df = split_into_periods(df, 'time')
        for period, name, color in zip(period_df, ["morning", "lunch", "evening"], ["#ab63fa", "#19d3f3", "#FF6692"]):
            mean = period['value'].mean()
            q1 = period['value'].quantile(0.25)
            q3 = period['value'].quantile(0.75)
            fig.add_trace(go.Violin(y=period["value"], name=name, box_visible=True,
                                    meanline_visible=True, marker_color=color))

            # fig.add_annotation(x=name, y=mean, xref="x", yref="y", text=f"{mean:.2f}", showarrow=False)
            for q in [q1, q3]:
                fig.add_annotation(x=name, y=q, xref="x", yref="y", text=f"{q:.1f}", showarrow=False, borderpad=1,
                                   bgcolor=annotation_bg_color, font=dict(size=14, color=color),)

        fig.update_layout(title='Insulin Violin Plot')
        # fig.update_yaxes(showgrid=True, gridcolor='#87aad6')
        # fig.update_yaxes(tickvals=[3, 5, 6, 7, 8, 9, 11, 13, 15])
        fig.update_layout(height=400)
        fig.update_layout(showlegend=False)

        return html.Div([dcc.Graph(figure=fig)])

    return html.Div(id=ids.INSULIN_VIOLIN_GRAPH)
