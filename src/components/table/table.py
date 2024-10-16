from dash import Dash, html
from src.const import *
from datetime import datetime
from src.table_generator.GlucoseTableGenerator import GlucoseTableGenerator
from . import ids
from dash.dependencies import Input, Output, State
import os, random


def render(app: Dash) -> html.Div:
    language = 'en'

    
    @app.callback(
        Output(ids.TABLE_CONTAINER, 'children'),
        State(ids.DATE_PICKER, 'start_date'),
        State(ids.DATE_PICKER, 'end_date'),
        Input(ids.UPDATE_TABLE, 'n_clicks')
    )
    def render_table_to_html(start_date, end_date, n_clicks)->html.Div:
        for file in os.listdir('assets/table'):
            if 'glucose' in file and '.html' in file:
                os.remove(os.path.join('assets','table', file))
        
        source_file = f'assets/table/glucose_{random.randint(10000, 99999)}.html'
        if start_date is None or end_date is None:
            return html.Div('empty')
        
        start_date = datetime.fromisoformat(start_date)
        end_date = datetime.fromisoformat(end_date)
        if start_date > end_date:
            return html.Div('empty')
        
        table_generator = GlucoseTableGenerator(
            reading_folder=DATA_FOLDER, language=language, insulin_folder=INSULIN_FOLDER)
        loading_sucess = table_generator.load_data(start_date=start_date, end_date=end_date)
        if not loading_sucess:
            return html.Div('Error')
        table_generator.to_html(source_file, dark_bkg=True)
        
        return html.Div(
            children=[
                html.Iframe(
                    src=source_file,
                    style={"width": "100%", "height": "1024px"},
                )
            ])
    
    return html.Div('Loading...',id=ids.TABLE_CONTAINER)
