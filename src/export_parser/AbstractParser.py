import pandas as pd
import os
from typing import Protocol
from src.const import *


class AbstractParser(Protocol):

    @property
    def insulin(self) -> pd.DataFrame | None:
        """Returns insulin dataframe."""

    @property
    def glucose(self) -> pd.DataFrame | None:
        """Returns glucose dataframe."""

    def _get_trend(self, glucose_values: pd.Series, datetime: "pd.Series[pd.Timestamp]") -> tuple[pd.Series, pd.Series, pd.Series]:
        df = pd.DataFrame({'datetime': datetime, 'values': glucose_values})
        df['value_delta'] = df['values'].diff() / (df['datetime'].diff().dt.total_seconds() / 60)  # type: ignore
        df['trend'] = pd.cut(df['value_delta'], DEXCOM_TREND_MAPPINGS_MMOL_L[::-1], right=True,
                             labels=[val for val in range(1, 8)][::-1])
        df = df.drop(axis=1, labels='value_delta')
        df['trend'] = df['trend'].cat.add_categories(0).fillna(0)  # type: ignore
        df['trend_description'] = df['trend'].map(lambda x: DEXCOM_TREND_DESCRIPTIONS[x])
        df['trend_arrow'] = df['trend'].map(lambda x: DEXCOM_TREND_ARROWS[x])
        return df['trend'], df['trend_description'], df['trend_arrow']

    def save_glucose_to_separate_files(self, folder: str) -> None:
        if self.glucose is None:
            raise NotImplementedError("Property *glucose* must be impelmented as pd.Dataframe.")
        for date, group in self.glucose.groupby('day'):
            day, month, year = date.split('-')
            subdir = os.path.join(folder, f'{year}', f'{month}')
            filename = os.path.join(subdir, f'{year}-{month}-{day}.csv')
            if not os.path.exists(subdir):
                os.makedirs(subdir)
            new_df = group.astype(str)
            if os.path.isfile(filename):
                df = pd.read_csv(filename, dtype=str)
                df = pd.concat([df, new_df]).drop_duplicates().sort_values(by="time")
            else:
                df = new_df.drop_duplicates().sort_values(by="time")
            df.to_csv(filename, index=False, header=True)

    def save_insulin_to_separate_files(self, folder: str) -> None:
        if self.insulin is None:
            raise NotImplementedError("Property *insulin* must be impelmented as pd.Dataframe.")
        if not os.path.exists(folder):
            os.makedirs(folder)
        for date in self.insulin['day'].map(lambda x: x[3:]).unique():
            month, year = date.split('-')
            new_df = self.insulin[self.insulin['day'].str.contains(date)]
            new_df['d'] = new_df['day'].map(lambda x: x[:2])
            subdir = os.path.join(folder, f'{year}')
            filename = os.path.join(subdir, f'{year}-{month}.csv')
            if not os.path.exists(subdir):
                os.makedirs(subdir)
            new_df = new_df.astype(str)
            if os.path.isfile(filename):
                df = pd.read_csv(filename, dtype=str)
                df['d'] = df['day'].map(lambda x: x[:2])
                df = pd.concat([df, new_df]).drop_duplicates().sort_values(by=['d', 'time'])
            else:
                df = new_df.drop_duplicates().sort_values(by=['d', 'time'])
            df = df.drop(['d'], axis=1)
            df.to_csv(filename, index=False, header=True)
