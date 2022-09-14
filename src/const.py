
DEXCOM_EXPORT_FOLDER = 'data/dexcom_export'
DATA_FOLDER = 'data/glucose'
INSULIN_FOLDER = 'data/insulin'


# DEXCOM_EXPORT_FOLDER = '/Volumes/home/diabetes_data/dexcom_export'
# DATA_FOLDER = '/Volumes/home/diabetes_data/glucose'
# INSULIN_FOLDER = '/Volumes/home/diabetes_data/insulin'


RANGE = [10.0, 3.9]

def check_range(x):
    if x > RANGE[0] :
        return 'high'
    elif x < RANGE[1]:
        return 'low'
    else:
        return 'ok'

GLUCOSE_RELOAD_INTERVAL = 1*60  # in seconds

color_map = {'high': '#FFA15A', 'low': '#EF553B', 'ok': '#00cc96'}

DEXCOM_TREND_DESCRIPTIONS = [
    "",
    "rising quickly",
    "rising",
    "rising slightly",
    "steady",
    "falling slightly",
    "falling",
    "falling quickly",
    "unable to determine trend",
    "trend unavailable",
]
DEXCOM_TREND_DIRECTIONS = {
    "None": 0,  # unconfirmed
    "DoubleUp": 1,
    "SingleUp": 2,
    "FortyFiveUp": 3,
    "Flat": 4,
    "FortyFiveDown": 5,
    "SingleDown": 6,
    "DoubleDown": 7,
    "NotComputable": 8,  # unconfirmed
    "RateOutOfRange": 9,  # unconfirmed
}

DEXCOM_TREND_ARROWS = ["", "↑↑", "↑", "↗", "→", "↘", "↓", "↓↓", "?", "-"]
MMOL_L_CONVERTION_FACTOR = 0.0555
DEXCOM_TREND_MAPPINGS_MG_DL = [8, 3., 2., 1., -1., -2., -3., -8]
DEXCOM_TREND_MAPPINGS_MMOL_L = [val*MMOL_L_CONVERTION_FACTOR for val in DEXCOM_TREND_MAPPINGS_MG_DL]

PERIODS: list[tuple[str, str]] = [
    ('06:00:00', '10:00:00'),
    ('11:00:00', '15:00:00'),
    ('17:00:00', '21:30:00'),
    ('21:30:00', '23:59:59'),
]

INDEX_NAMES: list[str] = ['rok', 'mesiac', 'čas', 'deň']
PERIOD_LABELS: list[str] = ['ráno', 'obed', 'večer', 'noc']
MONTHS: list[str] = ['január', 'február', 'marec', 'apríl', 'máj', 'jún',
                     'júl', 'august', 'september', 'október', 'november', 'december']

INDEX_NAMES_EN: list[str] = ['year', 'month', 'time', 'days']
PERIOD_LABELS_EN: list[str] = ['morning', 'lunch', 'dinner', 'night']
MONTHS_EN: list[str] = ['january', 'february', 'march', 'april', 'may', 'june',
                        'july', 'august', 'september', 'october', 'november', 'december']

HTML_HEADER = """
<!DOCTYPE html>
<html lang="sk">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Glucose Table</title>
</head>
<body>
"""

HTML_FOOTER = """
</body>
</html>
"""
