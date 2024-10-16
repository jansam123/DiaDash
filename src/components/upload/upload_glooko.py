from dash import Dash, html, dcc, DiskcacheManager
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from . import ids
from src.const import *
import base64
import os, io
from src.export_parser.GlookoParser import GlookoParser
import datetime
# from src.sensor_export_parser.DexcomParser import DexcomParser
# import diskcache
# cache = diskcache.Cache("./cache")
# background_callback_manager = DiskcacheManager(cache)

def render(app: Dash) -> html.Div:

    def parse_content(content: str, filename: str, date: str) -> bool:
        if filename[-4:] != '.csv':
            return False
        _, content_string = content.split(',')
        decoded = base64.b64decode(content_string)
        with open(os.path.join(GLOOKO_EXPORT_FOLDER, filename.replace('.csv', '')+'_'+date+'.csv'), 'w+') as f:
            f.write(io.StringIO(decoded.decode('utf-8')).getvalue())
        return True

    @app.callback(
        Output(ids.UPLOAD_SUCESS_GLOOKO, 'children'),
        Input(ids.UPLOAD_DATA_GLOOKO, 'contents'),
        State(ids.UPLOAD_DATA_GLOOKO, 'filename'),
        State(ids.UPLOAD_DATA_GLOOKO, 'last_modified'),
        prevent_initial_call=True,
        )
    def update_output(list_of_contents, list_of_names, list_of_dates)->html.Div:
        if list_of_contents is None:
            return html.Div([html.Span('Error', className='badge bg-danger')])
        for content, name, date in zip(list_of_contents, list_of_names, list_of_dates):
            # convert int date to string datetime format
            date = datetime.datetime.fromtimestamp(date).strftime('%Y-%m-%d_%H-%M-%S')
            print(date)
            out = parse_content(content, name, date)
            if not out:
                return html.Div([html.Span('Error', className='badge bg-danger')])
            
            parser = GlookoParser(os.path.join(GLOOKO_EXPORT_FOLDER, name.replace('.csv', '')+'_'+date+'.csv'))
            parser.save_insulin_to_separate_files(INSULIN_FOLDER)
            # parser.save_glucose_to_separate_files(DATA_FOLDER)
            
        return html.Div([html.Span('Done', className='badge bg-success')])

    return html.Div([
        html.Div([
            dbc.Row([
                dbc.Col(html.Div([html.H5('Import Glooko Data', className='card-title'), ]), width=8,  align="start"),
                dbc.Col(html.Div(id=ids.UPLOAD_SUCESS_GLOOKO), width=1,  align="start"),
                dbc.Col(html.Img(src='assets/images/glooko.png', style={'height': '30px'}), width=3,  align="start"),
            ]),
            html.Div([
                dcc.Upload(
                    id=ids.UPLOAD_DATA_GLOOKO,
                    children=html.Div([html.I(className="fa-solid fa-cloud-arrow-up"),
                        ' Drag and Drop or ',
                        html.A('Select Files', className='text-primary')
                    ]),
                    style={
                        'width': '100%',
                        'height': '100%',
                        'lineHeight': '40px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                    },
                    multiple=True
                ),
                html.Div(id='output-data-upload-glooko'),
            ]),
        ], className='card-body'),
    ], className='card border-primary')
