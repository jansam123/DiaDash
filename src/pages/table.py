import dash
from src.components.table.layout import create_layout


dash.register_page(__name__, path='/table')
layout = create_layout(dash.get_app())
