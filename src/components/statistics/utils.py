from src.const import *
import pandas as pd
from datetime import datetime


def split_into_periods(df, time_col):
    period_df = []
    for period in PERIODS[:-1]:
            start = datetime.strptime(period[0], "%H:%M:%S").time()
            end = datetime.strptime(period[1], "%H:%M:%S").time()
            qq_df = df.query(f"{time_col} >= @start and {time_col} <= @end")
            period_df.append(qq_df)
    return period_df