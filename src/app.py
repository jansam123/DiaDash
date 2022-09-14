from dash import Dash
import flask
from src.const import *
import dash_bootstrap_components as dbc
from src.components.layout import create_layout



server = flask.Flask(__name__)
app = Dash(__name__, use_pages=True, server=server, assets_folder='../assets', external_stylesheets=[dbc.icons.FONT_AWESOME])
app.title = 'Glucose'
app.layout = create_layout(app)


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)
