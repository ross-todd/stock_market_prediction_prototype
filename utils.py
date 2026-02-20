# utils.py — Helpers Layer
# Constants, colours, date calculations, and custom styling

from datetime import datetime
from pandas.tseries.offsets import BDay


# ── Ticker Constants ──────────────────────────────────────────────────────────

TICKERS = {
    "Barclays plc":               "BARC.L",
    "HSBC Holdings plc":          "HSBA.L",
    "Lloyds Banking Group plc":   "LLOY.L"
}

TICKER_LIST     = list(TICKERS.values())
COMPANY_OPTIONS = ["All Companies"] + list(TICKERS.keys())


# ── Colour Constants ──────────────────────────────────────────────────────────

BANK_COLOR_MAP = {
    "BARC.L": "#0000FF",   # Barclays — blue
    "HSBA.L": "#FF0000",   # HSBC — red
    "LLOY.L": "#008000",   # Lloyds — green
}


# ── Date Calculation ──────────────────────────────────────────────────────────

# Returns a start date based on a preset range label
def get_start_date_from_range(range_selection: str):
    today = datetime.now()
    mapping = {
        '1D': BDay(1),
        '1W': BDay(5),
        '1M': BDay(21),
        '3M': BDay(63),
        '6M': BDay(126),
        '1Y': BDay(252),
        '5Y': BDay(5 * 252),
    }
    offset = mapping.get(range_selection, BDay(21))
    return today - offset


# ── Custom Styling ────────────────────────────────────────────────────────────

GLOBAL_CSS = """
<style>
    .stMainBlockContainer { padding-bottom: 0rem !important; }
    .stVerticalBlock { padding-bottom: 0rem !important; }
    .stPlotlyChart { margin-bottom: 0rem !important; }
</style>
"""

DATE_RANGE_BUTTONS_CSS = """
<style>
    div[data-testid="stHorizontalBlock"] {
        min-height: 50px !important;
        max-height: 50px !important;
        margin-top: -5px !important;
        margin-bottom: 10px !important;
    }
    div[data-testid="stHorizontalBlock"] > div {
        min-height: 50px !important;
    }
    button[kind="primary"] {
        background-color: #FFD700 !important;
        color: black !important;
        border: 2px solid #FFA500 !important;
        font-weight: 600 !important;
        transition: none !important;
        box-shadow: inset 0 0 0 1px rgba(0,0,0,0.1) !important;
    }
    button[kind="secondary"] {
        background-color: #f0f2f6 !important;
        color: #666 !important;
        border: 1px solid #ddd !important;
        transition: none !important;
        font-weight: 400 !important;
    }
    div[data-testid="column"] button {
        height: 38px !important;
        min-height: 38px !important;
        max-height: 38px !important;
        padding: 0.25rem 0.75rem !important;
        margin: 5px 0 !important;
        width: 100% !important;
    }
    button:focus {
        outline: 2px solid #FFD700 !important;
        box-shadow: inset 0 0 0 1px rgba(0,0,0,0.1) !important;
    }
    div[data-testid="column"] { min-width: 0 !important; }
    .stPlotlyChart { min-height: 670px; margin-top: 10px !important; }
    button p { margin: 0 !important; white-space: nowrap !important; }
</style>
"""

