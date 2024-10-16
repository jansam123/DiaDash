from datetime import datetime
from typing import Optional
import pandas as pd
import numpy as np
import os
import argparse
from src import const
from pandas.io.formats.style import Styler
from src.data.loader import get_glucose_data, get_insulin_data
from io import StringIO


class GlucoseTableGenerator():

    def __init__(self, reading_folder: str, language: str = 'sk', insulin_folder: str = None) -> None:
        if language == 'sk':
            self.index_names = const.INDEX_NAMES
            self.period_labels = const.PERIOD_LABELS
            self.months = const.MONTHS
            self.event_type = const.EVENT_TYPE
        elif language == 'en':
            self.index_names = const.INDEX_NAMES_EN
            self.period_labels = const.PERIOD_LABELS_EN
            self.months = const.MONTHS_EN
            self.event_type = const.EVENT_TYPE_EN
        else:
            raise ValueError("Language must be either 'sk' or 'en'")

        self._reading_folder = reading_folder
        self._insulin_folder = insulin_folder


    @ property
    def data(self) -> pd.DataFrame:
        return self._data

    @ property
    def insulin_data(self) -> pd.DataFrame:
        return self._insulin_data
    
    def load_data(self, start_date: str | datetime = None, end_date: str | datetime = None) -> bool:
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%d-%m-%Y") if start_date is not None else None
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%d-%m-%Y") if end_date is not None else None
        _data = self._read_data(self._reading_folder, start_date, end_date)
        if _data is None:
            return False
        _data = self._generate_diary_format(_data, 'mean')
        _data = self._generate_multiindex_format(_data)
        
        if self._insulin_folder is not None:
            _insulin_data = self._read_insulin_data(self._insulin_folder, start_date, end_date)
            if _insulin_data is not None:
                _insulin_data = self._generate_diary_format(_insulin_data, 'sum')
                self._insulin_data = self._generate_multiindex_format(_insulin_data)
                # align the dataframes
                self._insulin_data = self._insulin_data.align(_data)[0]
                _data = pd.concat([_data, self._insulin_data], axis=1, keys=[1,0])
                _data = _data.reorder_levels([1, 2, 0, 3], axis=1)
                _data = _data.sort_index(axis=1, level=[1, 0, 2])
            else:
                self._insulin_data = _data.copy()
                self._insulin_data[:] = np.nan
                _data = pd.concat([_data, self._insulin_data], axis=1, keys=[1,0])
                _data = _data.reorder_levels([1, 2, 0, 3], axis=1)
                _data = _data.sort_index(axis=1, level=[1, 0, 2])
        self._data = self._rename_columns(_data)
        return True

    def _read_data(self, folder: str, start_date: datetime, end_date: datetime) -> pd.DataFrame| None:
        df = get_glucose_data(end_date, start_date, folder)
        if df is None:
            return None
        df = df[["mmol_l", "time", "day"]]
        df = df.rename(columns={"mmol_l": "value"})
        df["datetime"] = pd.to_datetime(df["day"]+' '+df["time"], format='%d-%m-%Y %H:%M:%S')
        df = df.sort_values(by="datetime", ascending=True)
        return df

    def _read_insulin_data(self, folder: str, start_date: Optional[datetime], end_date: Optional[datetime]) -> pd.DataFrame:
        df = get_insulin_data(end_date, start_date, folder)
        if df is None:
            return None
        df = df[["time", "day", "value", "primed"]]
        df = df[df["primed"] == False].drop(columns=["primed"])
        df["datetime"] = pd.to_datetime(df["day"]+' '+df["time"], format='%d-%m-%Y %H:%M:%S')
        df = df.sort_values(by="datetime", ascending=True)
        return df

    def _between_times(self, df: pd.DataFrame, start_time: datetime, end_time: datetime, label: Optional[str] = None, operation: str = 'mean') -> pd.DataFrame:
        df['time'] = df['datetime'].dt.time
        start_time = start_time.time()
        end_time = end_time.time()
        df = df.query("time >= @start_time and time <= @end_time")
        df = df.groupby(['day'])[['value']].agg({'value': operation})

        df['time'] = start_time.strftime("%H:%M:%S") if label is None else label
        df = df.reset_index()
        return df

    def _generate_diary_format(self, df: pd.DataFrame, operation='mean') -> pd.DataFrame:
        final_df = pd.DataFrame()
        final_df["day"] = df["day"].unique()
        final_df = final_df.set_index("day")
        for i, period in enumerate(const.PERIODS):
            start = datetime.strptime(period[0], "%H:%M:%S")
            end = datetime.strptime(period[1], "%H:%M:%S")
            period_df = self._between_times(df, start, end, operation=operation)
            period_df = period_df.drop(columns=["time"])
            period_df = period_df.rename(columns={"value": i}).set_index("day")
            final_df = final_df.join(period_df)
        final_df = final_df.reset_index()
        del df
        return final_df

    def _generate_multiindex_format(self, df: pd.DataFrame, language: str = 'sk') -> pd.DataFrame:

        df[[self.index_names[3], self.index_names[1], self.index_names[0]]
           ] = df['day'].str.split('-', expand=True).astype(int)
        df = df.drop(['day'], axis=1)
        df = df.set_index(self.index_names[3])
        df = df.pivot(columns=[self.index_names[1], self.index_names[0]]).swaplevel(i=2, j=0, axis=1).sort_index(
            axis=1, level=0)
        # df.columns.names = self.index_names[:-1]
        return df

    def _rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.rename(columns=lambda x: self.months[x-1], level=1)
        df = df.rename(columns=lambda x: self.period_labels[x], level=3)
        if df.columns.nlevels == 4:
            df = df.rename(columns=lambda x: self.event_type[x], level=2)
        df.index.name = None
        df.columns.names = [None for _ in range(df.columns.nlevels)]
        lst = [(f'{i}   {j}', k, l) for i, j, k, l in df.columns]
        df.columns = pd.MultiIndex.from_tuples(lst)
        return df

    def _make_pretty(self, df: pd.DataFrame, dark_bkg: bool = True) -> Styler:
        def high_low(entry):
            if entry >= 10 and entry < 13:
                return 'high'
            elif entry < 4:
                return 'low'
            elif entry >= 13:
                return 'very-high'
            elif entry >= 4 and entry < 10:
                return 'ok'
            else:
                return 'nan'

        glucose_range = df.map(high_low)
        glucose_range = glucose_range.T
        glucose_range.loc[(slice(None), self.event_type[0]  ,slice(None)), :] = glucose_range.loc[(slice(None), self.event_type[0], slice(None)), :].map(lambda x: 'i' if x != 'nan' else 'nan')
        glucose_range = glucose_range.T

        
        s = df.style.format(na_rep='', formatter="{:5.1f}".format)
        font_family = 'SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;'
        font_family_sans = 'Roboto, -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Arial, sans-serif;'

        table_styles = [
            # Hover effect on cells
            {'selector': 'td:hover', 'props': [('background-color', '#ffffb3')]},

            # Style for index names
            {'selector': '.index_name', 'props': 'font-style: italic; color: black; font-weight:normal; background-color: #b1d7ea'},

            # Header styles
            {'selector': 'th:not(.index_name)', 'props': f'background-color: #242424; color: white; font-family:{font_family};'},
            {'selector': 'th.col_heading', 'props': 'text-align: center;'},
            {'selector': 'th.col_heading.level0', 'props': 'font-size: 20px;'},
            {'selector': 'th.col_heading.level2', 'props': 'font-size: 10px;'},

            {
                'selector': 'td, th',
                'props': [
                    ('font-family', font_family_sans),
                    ('width', '35px'),       # Fixed width
                    ('min-width', '35px'),   # Minimum width
                    ('max-width', '35px'),   # Maximum width
                    ('height', '35px'),      # Fixed height
                    ('min-height', '35px'),  # Minimum height
                    ('max-height', '35px'),  # Maximum height
                    ('font-size', '16px'),
                    ('text-align', 'center'),  # Center text horizontally
                    ('vertical-align', 'middle'),  # Center text vertically
                    ('box-sizing', 'content-box'),  # Exclude padding/border from size
                    # ('border', '1px solid black')  # Add a thin border to confirm cell boundaries
                ]
            },
            # set td bold
            {'selector': 'td', 'props': 'font-weight: bold;'},

            # Cell background colors based on content
            {'selector': '.high', 'props': 'background-color: #ffeb9c; color: #9c6500;'},
            {'selector': '.low', 'props': 'background-color: #FFC7CE; color: #9C0006;'},
            {'selector': '.very-high', 'props': 'background-color: #FABF8F; color: #974706;'},
            {'selector': '.ok', 'props': 'background-color: #C6EFCE; color: #006100;'},
            {'selector': '.nan', 'props': 'background-color: #D3D3D3;'},
            {'selector': '.i', 'props': 'background-color: #c4e5f5; color: #010f5c;'},
        ]

        # Apply the unified styles to the dataframe
        s = s.set_table_styles(table_styles)
        s = s.set_td_classes(glucose_range)
        return s

    def to_html(self, file_name: str, dark_bkg:bool = True) -> str:
        main_str = ''
        # for level0_col in self._data.columns.get_level_values(0).unique():
        string_buf = StringIO()
        styler = self._make_pretty(self._data, dark_bkg)
        styler.to_html(string_buf)
        main_str += string_buf.getvalue()
        with open(file_name, 'a+') as f:
            content = main_str
            # f.seek(0, 0)
            # f.write(const.HTML_HEADER.rstrip('\r\n') + '\n' + content + const.HTML_FOOTER.rstrip('\r\n'))
            f.write(content)

    def to_pdf(self, file_name: str) -> None:
        from src.table_generator.utils import html_to_pdf
        tmp_file_name = 'assets/tmp_html_file.html'
        self.to_html(tmp_file_name)
        html_to_pdf(tmp_file_name, file_name)
        if os.path.exists(tmp_file_name):
            os.remove(tmp_file_name)

    def to_excel(self, file_name: str):

        with pd.ExcelWriter(
            file_name,
            date_format="YYYY-MM-DD",
            datetime_format="YYYY-MM-DD HH:MM:SS",
            engine='xlsxwriter'
        ) as writer:

            self._data.to_excel(writer, na_rep='')
            # num_months = len(self.data.columns.get_level_values(self.index_names[1]).unique())
            # workbook = writer.book
            # worksheet = writer.sheets['Sheet1']

            # red_format = workbook.add_format({'bg_color': '#FFC7CE',
            #                                   'font_color': '#9C0006'})
            # green_format = workbook.add_format({'bg_color': '#C6EFCE',
            #                                     'font_color': '#006100'})
            # yellow_format = workbook.add_format({'bg_color': '#ffeb9c',
            #                                      'font_color': '#9c6500'})
            # orange_format = workbook.add_format({'bg_color': '#FABF8F',
            #                                      'font_color': '#974706'})
            # gray_format = workbook.add_format({'bg_color': '#D3D3D3'})

            # worksheet.conditional_format(4, 1, 34, num_months*8, {'type':     'blanks',
            #                                                       'format':   gray_format})
            # worksheet.conditional_format(4, 1, 34, num_months*8, {'type':     'cell',
            #                                                       'criteria': '<',
            #                                                       'value':    4,
            #                                                       'format':   red_format})
            # worksheet.conditional_format(4, 1, 34, num_months*8, {'type':     'cell',
            #                                                       'criteria': 'between',
            #                                                       'minimum':  4,
            #                                                       'maximum':  10,
            #                                                       'format':   green_format})
            # worksheet.conditional_format(4, 1, 34, num_months*8, {'type':     'cell',
            #                                                       'criteria': '>',
            #                                                       'value':    13,
            #                                                       'format':   orange_format})
            # worksheet.conditional_format(4, 1, 34, num_months*8, {'type':     'cell',
            #                                                       'criteria': '>',
            #                                                       'value':    10,
            #                                                       'format':   yellow_format})


def main(args: argparse.Namespace):
    table_generator = GlucoseTableGenerator(reading_folder=args.folder, insulin_folder=args.insulin_folder)
    loading_sucess = table_generator.load_data(start_date=args.start_date, end_date=args.end_date)

    table_generator.to_html('assets/table.html')
    # table_generator.to_pdf('assets/table.pdf')
    # print(data_parser.data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", default="/Volumes/home/diabetes_data/glucose",
                        type=str, help="Folder containing the glucose data")
    parser.add_argument("--insulin_folder", default="/Volumes/home/diabetes_data/insulin",
                        type=str, help="Folder containing the insulin data")
    parser.add_argument("--start_date", default='01-05-2022', type=str,
                        help="Start date of the data in format '%d-%m-%Y'")
    parser.add_argument("--end_date", default='29-06-2022', type=str, help="End date of the data in format '%d-%m-%Y'")

    args = parser.parse_args([] if "__file__" not in globals() else None)
    main(args)
