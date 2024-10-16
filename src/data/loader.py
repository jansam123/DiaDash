from datetime import datetime, timedelta
import pandas as pd
import os

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


def get_glucose_data(start: datetime, end: datetime, folder: str, cols: list[str] | None = None) -> pd.DataFrame | None:
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
            read_csv_files.append(pd.read_csv(filename, dtype=GLUCOSE_DATA_SCHEMA, usecols=cols))
    if len(read_csv_files) == 0:
        return None
    df = pd.concat(read_csv_files)
    df["datetime"] = pd.to_datetime(df["day"]+' '+df["time"], format='%d-%m-%Y %H:%M:%S')
    return df.reset_index()


def get_insulin_data(start: datetime, end: datetime, folder: str, cols: list[str] | None = None) -> pd.DataFrame | None:
    read_csv_files = []
    for date in pd.date_range(start=end, end=start + timedelta(days=1), freq='MS').to_list():
        year = date.strftime('%Y')
        filename = os.path.join(folder, year, f"{date.strftime('%Y-%m')}.csv")
        if os.path.isfile(filename):
            read_csv_files.append(pd.read_csv(filename, dtype=INSULIN_DATA_SCHEMA, usecols=cols))
    if start.strftime('%Y-%m') == end.strftime('%Y-%m'):
        if os.path.isfile(os.path.join(folder, start.strftime('%Y'), f"{start.strftime('%Y-%m')}.csv")):
            read_csv_files.append(pd.read_csv(os.path.join(folder, start.strftime('%Y'), f"{start.strftime('%Y-%m')}.csv"), dtype=INSULIN_DATA_SCHEMA, usecols=cols))
    if len(read_csv_files) == 0:
        return None
    df = pd.concat(read_csv_files)
    df["date_time"] = pd.to_datetime(df["day"]+' '+df["time"], format='%d-%m-%Y %H:%M:%S')
    df = df.query("date_time <= @start and date_time >= @end")
    df = df.rename(columns={"date_time": "datetime"})
    if df.empty:
        return None
    return df.reset_index()