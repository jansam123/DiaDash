import dash
from src.components.statistics.layout import create_layout


dash.register_page(__name__, path='/statistics')
layout = create_layout(dash.get_app())
