import pdfkit  # brew install Caskroom/cask/wkhtmltopdf, sudo apt install wkhtmltopdf

def html_to_pdf(html_file_name:str, file_name: str):
    options = {
        'page-size': 'A4',
        'orientation': 'landscape',
        'margin-top': '0.1in',
        'margin-right': '0.5in',
        'margin-bottom': '0.2in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'lowquality': False,
        'quiet': '',
        'custom-header': [
            ('Accept-Encoding', 'gzip')
        ],
        'cookie': [
            ('cookie-name1', 'cookie-value1'),
            ('cookie-name2', 'cookie-value2'),
        ],
        'no-outline': None
    }

    with open(html_file_name) as f:
        pdfkit.from_file(input=f, output_path=file_name, options=options)
    f.close()

