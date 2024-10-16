from dash import Dash, dcc, html
from src import const
from . import ids
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from . import figure_theme
import plotly.io as pio


def render(app: Dash) -> html.Div:

    @app.callback(
        Output(ids.TREND_GRAPH, 'children'),
        Input(ids.GLUCOSE_DATA_STORAGE, 'data'),
        Input(ids.THEME_TOGGLE_SWITCH, 'value'))
    def update_graph(data: dict, value: bool) -> html.Div:
        if data is None or not data:
            return html.Div('Error: No data available.')
        if value:
            pio.templates.default = "my_cyborg"
        else:
            pio.templates.default = "white_cyborg"

        df = pd.DataFrame(data)
        df = df[['time', 'mmol_l']]

        df['time'] = pd.to_datetime(df['time'], format='%H:%M:%S')
        df['seconds_of_day'] = df['time'].dt.hour * 3600 + df['time'].dt.minute * 60 + df['time'].dt.second
        bin_size = 1200  # 10 minutes in seconds
        df['time_bin'] = (df['seconds_of_day'] // bin_size) * bin_size
        df['time_bin'] = pd.to_datetime(df['time_bin'], unit='s').dt.time
        
        
        grouped = df.groupby('time_bin')['mmol_l'].agg(
            median='median',
            p25=lambda x: x.quantile(0.25),
            p75=lambda x: x.quantile(0.75),
            p10=lambda x: x.quantile(0.10),
            p90=lambda x: x.quantile(0.90)
        ).reset_index()
        
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=grouped['time_bin'], y=grouped['median'],
            mode='lines', name='Median',
            line=dict(color='cyan')
        ))

        # Add 25-75% shaded area
        fig.add_trace(go.Scatter(
            x=grouped['time_bin'].tolist() + grouped['time_bin'].tolist()[::-1], 
            y=grouped['p75'].tolist() + grouped['p25'].tolist()[::-1],
            fill='toself', fillcolor='rgba(0, 100, 255, 0.2)',
            line=dict(color='rgba(255,255,255,0)'), 
            showlegend=False, name='25-75% Percentile'
        ))

        # Add 10-90% shaded area
        fig.add_trace(go.Scatter(
            x=grouped['time_bin'].tolist() + grouped['time_bin'].tolist()[::-1], 
            y=grouped['p90'].tolist() + grouped['p10'].tolist()[::-1],
            fill='toself', fillcolor='rgba(0, 100, 255, 0.2)',
            line=dict(color='rgba(255,255,255,0)'), 
            showlegend=False, name='10-90% Percentile'
        ))
        
        fig.add_hline(y=5, line_width=1, line_color=const.color_map['low'])
        fig.add_hline(y=9, line_width=1, line_color=const.color_map['high'])
        
        fig.update_layout(
        title='Glucose Time Profile',
        xaxis_title='Time of Day',
        yaxis_title='Glucose (mmol/L)',
        xaxis=dict(
        tickformat='%H:%M',
        dtick=6,  # 1-hour intervals in milliseconds
        tickmode='linear',
        # tickformat='%H',  # Format to show hours only
        ticks='outside'
        ),
        height=300,
        showlegend=False,
        )


        return html.Div([dcc.Graph(figure=fig)])

    return html.Div(id=ids.TREND_GRAPH)
