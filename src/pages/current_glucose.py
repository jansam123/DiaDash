import dash
from src.components.current_glucose.layout import create_layout


dash.register_page(__name__, path='')
layout = create_layout(dash.get_app())
