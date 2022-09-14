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

        df['time'] = pd.to_datetime(df['time'])

        group = df.groupby(pd.Grouper(key='time', freq='15min'))
        df_mean = group.mean()
        mean = df_mean['mmol_l'].mean()
        
        fig = px.scatter(df_mean,
                         x=df_mean.index,
                         y=['mmol_l'],
                         trendline="lowess",
                         trendline_options=dict(frac=0.1),
                         trendline_color_override='#19d3f3',
                         )
        fig.data[0]['mode'] = 'none'
        fig.data[1]['line']['width'] = 3
        

        fig.add_trace(go.Bar(x=df_mean.index,
                             y=df_mean['mmol_l'] - mean,
                             base=mean,
                             marker=dict(
                                 color=df_mean['mmol_l'] - mean,
                                 colorscale=[(0.00, '#EF553B'),   (0.17, "#EF553B"),
                                             (0.17, "#fa8dac"), (0.25, "#fa8dac"),
                                             (0.25, "#aeaeae"),  (0.615, "#aeaeae"),
                                             (0.615, "#FECB52"),  (0.83, "#FECB52"),
                                             (0.83, "#FFA15A"),  (1.00, "#FFA15A"), ],
                             )))

        fig.add_annotation(
            text=f'Average:\n {mean:.1f} mmol/L',
            # yanchor="top",
            # xanchor="right",
            xref="paper", 
            yref="paper",
            y=0.98,
            x=1,
            font=dict(
                size=15,
                color='white'
            ),
            bgcolor='rgba(28,45,228,0.5)',
            bordercolor="#1c2de4",
            borderwidth=2,
            showarrow=False,
        )

        fig.update_layout(showlegend=False)
        fig.update_layout(title='Average Glucose')
        fig.update_layout(height=300)
        fig.update_layout(yaxis_title='Glucose (mmol/L)')
        fig.update_layout(xaxis={
            'tickformat': '%H:%M',
        })
        fig.add_hline(y=5, line_width=1, line_color=const.color_map['low'])
        fig.add_hline(y=9, line_width=1, line_color=const.color_map['high'])

        return html.Div([dcc.Graph(figure=fig)])

    return html.Div(id=ids.TREND_GRAPH)
