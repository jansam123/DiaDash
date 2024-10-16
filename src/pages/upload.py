import dash
from src.components.upload.layout import create_layout


dash.register_page(__name__, path='/upload')
layout = create_layout(dash.get_app())
