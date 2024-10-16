import pandas as pd
from src.const import *
from .AbstractParser import AbstractParser
import argparse

class GlookoParser(AbstractParser):
    def __init__(self, file: str) -> None:
        self._file = file
        self._df = self._parse(file=file)

    def _parse(self, file) -> pd.DataFrame:
        df = pd.read_csv(file, skiprows=1, header=0)
        df = df.rename(columns={'Timestamp': 'datetime'})
        df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M')
        return df

    @property
    def insulin(self) -> pd.DataFrame:
        insulin = self._df[['Total Insulin (U)', 'datetime']]
        insulin = insulin.rename(columns={'Total Insulin (U)': 'value'})
        insulin['type'] = 'Fast-Acting'
        insulin = insulin[['datetime', 'value', 'type']].astype(
            {'value': 'float32', 'type': str}).reset_index(drop=True)
        insulin['time'] = insulin['datetime'].map(lambda x: x.strftime('%H:%M:%S'))
        insulin['day'] = insulin['datetime'].map(lambda x: x.strftime('%d-%m-%Y'))
        insulin = insulin.drop(axis=1, labels='datetime')
        return self._detect_priming(insulin)

    def _detect_priming(self, df: pd.DataFrame) -> pd.DataFrame:
        '''
            df: pd.DataFrame - insulin data, containes columns 'value', 'time', 'day', 'type'
        '''
        df['datetime'] = pd.to_datetime(df['day'] + ' ' + df['time'], format='%d-%m-%Y %H:%M:%S')
        # sort by datetime
        df = df.sort_values(by='datetime')
        threshold = pd.Timedelta(minutes=3)
        time_diff = df['datetime'].diff()
        group_breaks = (time_diff > threshold).cumsum()
        df['group_breaks'] = group_breaks
        df['primed'] = True
        df.loc[df.groupby('group_breaks')['value'].idxmax(), 'primed'] = False
        return df.drop(columns=['datetime', 'group_breaks']).reset_index(drop=True)
    
        
    @property
    def glucose(self) -> pd.DataFrame:
        raise NotImplementedError("GlookoParser does not support glucose data")


def main(args: argparse.Namespace) -> None:
    parser = GlookoParser(args.glooko_path)
    parser.save_insulin_to_separate_files(args.folder)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", default="/Volumes/home/diabetes_data/tmp",
                        type=str, help="Folder containing the data")
    parser.add_argument("--glooko_path", default='/Volumes/home/diabetes_data/dexcom_export/Clarity_Export_Jankov%C3%BDch_Samuel_2022-06-27_060933.csv',
                        type=str, help="Path of CLarity file exported from website.")

    args = parser.parse_args([] if "__file__" not in globals() else None)
    main(args)
