from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from src.const import *
from datetime import datetime
import os
from . import ids
from dash.dependencies import Input, Output, State
from src.table_generator.GlucoseTableGenerator import GlucoseTableGenerator


def render(app: Dash) -> html.Div:
    # language = 'en'
    download_options = ['EXCEL', 'HTML', 'PDF']

    def download_wrapper(file_type):
        file_extension = 'xlsx' if file_type == 'excel' else file_type
        def download(start_date, end_date, n_clicks, language):
            start_date = datetime.fromisoformat(start_date)
            end_date = datetime.fromisoformat(end_date)
            for file in os.listdir('assets/downloads'):
                os.remove(f'assets/downloads/{file}')
            file_name = f'assets/downloads/glucose_table.{file_extension}'
            table_generator = GlucoseTableGenerator(
                reading_folder=DATA_FOLDER, language=language, insulin_folder=INSULIN_FOLDER)
            loading_sucess = table_generator.load_data(start_date=start_date, end_date=end_date)
            if not loading_sucess:
                return {'content': 'Error', 'filename': 'error.txt'}
            # getattr(table_generator, f'to_{file_type}')(file_name)
            if file_type == 'excel':
                table_generator.to_excel(file_name)
            elif file_type == 'html':
                table_generator.to_html(file_name, dark_bkg=False)
            elif file_type == 'pdf':
                table_generator.to_pdf(file_name)
            else:
                return {'content': 'Error', 'filename': 'error.txt'}
            return dcc.send_file(file_name)
        return download

    for dwn_opt in download_options:
        app.callback(
            Output(dwn_opt+'_'+ids.TABLE_DOWNLOAD, 'data'),
            State(ids.DATE_PICKER, 'start_date'),
            State(ids.DATE_PICKER, 'end_date'),
            Input(getattr(ids, dwn_opt+'_DOWNLOAD_BUTTON'), 'n_clicks'),
            State(ids.LANGUAGE_DROPDOWN, 'value'),
            prevent_initial_call=True
        )(download_wrapper(dwn_opt.lower()))

    save_buttons_className = "btn btn-primary text-center me-1"
    return html.Div([
        html.Div([
            dbc.Row([
                dbc.Col(html.H5('Save table', className='card-title'), width=9,  align="start"),
                dbc.Col(dcc.Dropdown(['sk', 'en'], value='sk', id=ids.LANGUAGE_DROPDOWN,
                                     className='mb-1', clearable=False), width=3,  align="start")
            ]),
            *[html.Button(option, id=getattr(ids, option+'_DOWNLOAD_BUTTON'), className=save_buttons_className, n_clicks=0)
              for option in download_options],
            *[dcc.Download(id=opt+'_'+ids.TABLE_DOWNLOAD) for opt in download_options],
        ], className='card-body'),
    ], className='card border-primary')
