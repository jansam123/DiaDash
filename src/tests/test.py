from datetime import datetime, timedelta
import pandas as pd
import os
from dash import Dash, dcc, html
from const import *
from components.statistics import ids
from dash.dependencies import Input, Output
from datetime import datetime, timedelta
import plotly.graph_objs as go
import pandas as pd


GLUCOSE_DATA_SCHEMA = {
    "mg_dl": int,
    "mmol_l": float,
    "trend": str,
    "trend_arrow": str,
    "time": str,
    "day": str,
}

INSULIN_DATA_SCHEMA = {
    "value": float,
    "type": str,
    "time": str,
    "day": str,
}


def get_glucose_data(start: datetime, end: datetime, folder: str) -> pd.DataFrame | None:
    """Generate glucose dataframe for selected date range.

    Args:
        start (datetime): Most recent day.
        end (datetime): Last day to include.
        folder (str, optional): Folder in which are readings of glucose stored. Defaults to 'data'. The files must be sorted into subfolders into years and months. The naming scheme is 'YYYY-MM-DD.csv'.

    Returns:
        pd.DataFrame: Glucose readings whithin the date range (including both start and end day).
    """
    read_csv_files = []
    for date in pd.date_range(start=end, end=start + timedelta(days=1)).to_list():
        month = date.strftime('%m')
        year = date.strftime('%Y')
        filename = os.path.join(folder, year, month, f"{date.strftime('%Y-%m-%d')}.csv")
        if os.path.isfile(filename):
            read_csv_files.append(pd.read_csv(filename, dtype=GLUCOSE_DATA_SCHEMA))
    if len(read_csv_files) == 0:
        return None
    df = pd.concat(read_csv_files)
    df["datetime"] = pd.to_datetime(df["day"]+' '+df["time"], format='%d-%m-%Y %H:%M:%S')
    return df.reset_index()


def load_24h_data(value) -> dict:
    df = get_glucose_data(datetime.now(), datetime.now() - timedelta(days=value), folder=DATA_FOLDER)
    if df is None:
        return df

    # df["range"] = df["mmol_l"].apply(lambda x: 'high' if x > RANGE[0] else 'low' if x < RANGE[1] else 'ok')
    return df


def update_graph(data: dict) -> dcc.Graph:
    # if data is None or not data:
    #     return html.Div([dcc.Graph(figure=px.scatter(template="plotly_dark"))], className='container-bigger')

    # df = pd.DataFrame(data, dtype={'time': 'datetime64[ns]'})
    df=data
    df = df[['datetime', 'mmol_l']]
    # df['datetime'] = df['datetime']
    # df['time'] = pd.to_datetime(df['time'])
    # print(df)
    # dfp = pd.pivot_table(df, index=pd.Grouper(key='time', freq='H'),
    #                      columns='range',
    #                      aggfunc=len,
    #                      fill_value=0)
    group = df.groupby(pd.Grouper(key='datetime', freq='15min'))
    df_mean = group.mean()
    # df_std = group.std()
    fig = go.Figure([
        go.Scatter(
            x=df_mean.index,
            y=df_mean['mmol_l'],
            # line=dict(color='rgb(0,100,80)'),
            mode='lines'
        ),
        go.Scatter(
            name='Upper Bound',
            x=df_mean.index,
            y=df_mean['mmol_l'],  # + df_std['mmol_l'],
            mode='lines',
            # marker=dict(color="#444"),
            line=dict(width=0),
            showlegend=False
        ),
        go.Scatter(
            name='Lower Bound',
            x=df_mean.index,
            y=df_mean['mmol_l'],  # - df_std['mmol_l'],
            # marker=dict(color="#444"),
            line=dict(width=0),
            mode='lines',
            # fillcolor='rgba(68, 68, 68, 0.3)',
            fill='tonexty',
            showlegend=False
        )
    ])
    fig.update_layout(template="plotly_dark")
    fig.update_layout(showlegend=False)
    fig.add_hline(y=RANGE[0], line_width=1, line_color=color_map['high'])
    fig.add_hline(y=RANGE[1], line_width=1, line_color=color_map['low'])

    return dcc.Graph(figure=fig)

def main():
    fig = update_graph(load_24h_data(120))
    
if __name__ == '__main__':
    main()