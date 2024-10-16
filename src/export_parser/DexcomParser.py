import pandas as pd
from src.const import *
from .AbstractParser import AbstractParser
import argparse

class DexcomParser(AbstractParser):
    def __init__(self, file: str) -> None:
        self._file = file
        self._df = self._parse(file=file)

    def _parse(self, file) -> pd.DataFrame:
        df = pd.read_csv(file, skiprows=list(range(1, 11)), header=0)
        df = df.rename(columns={'Timestamp (YYYY-MM-DDThh:mm:ss)': 'datetime'})
        df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%dT%H:%M:%S')
        return df

    @property
    def insulin(self) -> pd.DataFrame:
        insulin = self._df[self._df['Event Type'] == 'Insulin'].dropna(axis=1, how='any')
        insulin = insulin.rename(columns={'Insulin Value (u)': 'value', 'Event Subtype': 'type'})
        insulin = insulin[['datetime', 'value', 'type']].astype(
            {'value': 'float32', 'type': str}).reset_index(drop=True)
        insulin['time'] = insulin['datetime'].map(lambda x: x.strftime('%H:%M:%S'))
        insulin['day'] = insulin['datetime'].map(lambda x: x.strftime('%d-%m-%Y'))
        insulin = insulin.drop(axis=1, labels='datetime')
        insulin['primed'] = False
        return insulin

    @property
    def glucose(self) -> pd.DataFrame:
        glucose = self._df[self._df['Event Type'] == 'EGV'].dropna(axis=1, how='any')
        glucose = glucose.rename(columns={'Glucose Value (mmol/L)': 'mmol_l'})
        glucose = glucose[['datetime', 'mmol_l']]
        glucose['mmol_l'] = glucose['mmol_l'].replace({'Low': '2.0', 'High': '23.0'}).astype({'mmol_l': 'float64'})
        glucose['mg_dl'] = (glucose['mmol_l'] / MMOL_L_CONVERTION_FACTOR).round(0)
        glucose = glucose.astype({'mmol_l': 'float32', 'mg_dl': 'int32'})
        glucose['trend'], glucose['trend_description'], glucose['trend_arrow'] = self._get_trend(
            glucose['mmol_l'], glucose['datetime'])
        glucose['time'] = glucose['datetime'].dt.strftime('%H:%M:%S')
        glucose['day'] = glucose['datetime'].dt.strftime('%d-%m-%Y')
        glucose = glucose.drop(axis=1, labels='datetime')
        glucose.insert(0, 'mg_dl', glucose.pop('mg_dl'))
        return glucose


def main(args: argparse.Namespace) -> None:
    parser = DexcomParser(args.clarity_path)
    parser.save_glucose_to_separate_files(args.folder)
    parser.save_insulin_to_separate_files(args.folder)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", default="/Volumes/home/diabetes_data/tmp",
                        type=str, help="Folder containing the data")
    parser.add_argument("--clarity_path", default='/Volumes/home/diabetes_data/dexcom_export/Clarity_Export_Jankov%C3%BDch_Samuel_2022-06-27_060933.csv',
                        type=str, help="Path of CLarity file exported from website.")

    args = parser.parse_args([] if "__file__" not in globals() else None)
    main(args)
