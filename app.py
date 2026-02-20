# app.py — Presentation Layer
# Full home screen: multi-company chart, date range buttons, data table, sidebar

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(__file__))

from utils import (
    TICKERS, TICKER_LIST, COMPANY_OPTIONS,
    BANK_COLOR_MAP, get_start_date_from_range,
    GLOBAL_CSS, DATE_RANGE_BUTTONS_CSS
)
from data import StockDataService


# ── Page Configuration ────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Stock Market Prediction - UK Banking Sector",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ── Session State Initialisation ──────────────────────────────────────────────

if 'start_date' not in st.session_state:
    st.session_state['start_date'] = get_start_date_from_range('1M').date()
if 'end_date' not in st.session_state:
    st.session_state['end_date'] = datetime.now().date()
if 'active_range' not in st.session_state:
    st.session_state['active_range'] = '1M'
if 'selected_company' not in st.session_state:
    st.session_state['selected_company'] = next(iter(TICKERS.keys()))


# ── Global CSS ────────────────────────────────────────────────────────────────

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  HOME SCREEN
# ══════════════════════════════════════════════════════════════════════════════

# Renders the home screen — range buttons, chart, and data table
class HomeScreen:

    def __init__(self, selected_company: str):
        self.selected_company = selected_company

    # Fetches data, current price info, and renders all components
    def render(self):
        st.markdown(DATE_RANGE_BUTTONS_CSS, unsafe_allow_html=True)

        self._render_range_buttons()

        df = StockDataService.get_stock_data(
            TICKER_LIST,
            st.session_state['start_date'].strftime('%Y-%m-%d'),
            st.session_state['end_date'].strftime('%Y-%m-%d')
        )

        if df is None:
            st.error("Unable to fetch data. Please check your internet connection.")
            return

        if df.empty:
            st.warning("No data available for the selected date range.")
            return

        # Fix 1 — safely extract Close prices, falling back to full df if not MultiIndex
        if isinstance(df.columns, pd.MultiIndex) and 'Close' in df.columns.get_level_values(0):
            df_close = df['Close'].copy()
        else:
            df_close = df

        current_info = self._get_current_info(df_close)

        self._render_chart(df_close, current_info)
        self._render_data_table()

    # Gets the latest closing price and date from the fetched DataFrame for the chart subtitle
    def _get_current_info(self, df_close: pd.DataFrame) -> str:
        if self.selected_company == "All Companies":
            return "Multiple companies selected"

        ticker = TICKERS.get(self.selected_company)
        if not ticker:
            return "Company not found"

        try:
            if df_close is not None and not df_close.empty and ticker in df_close.columns:
                close_prices = df_close[ticker].dropna()
                if not close_prices.empty:
                    price_str = f"{close_prices.iloc[-1]:.2f}p"
                    date_str  = close_prices.index[-1].strftime('%d %b %Y')
                    return f"Current: {price_str} ({date_str})"
        except Exception as e:
            # Fix 3 — log exception rather than silently passing
            st.warning(f"Could not fetch current price: {e}")

        return "Current price unavailable"

    # Renders the 1D–5Y date range toggle buttons
    def _render_range_buttons(self):
        range_labels = ['1D', '1W', '1M', '3M', '6M', '1Y', '5Y']
        with st.container():
            cols = st.columns(len(range_labels))
            for col, label in zip(cols, range_labels):
                with col:
                    btn_type = "primary" if st.session_state['active_range'] == label else "secondary"
                    if st.button(label, key=f"range_{label}", type=btn_type, use_container_width=True):
                        st.session_state['active_range'] = label
                        st.session_state['start_date'] = get_start_date_from_range(label).date()
                        st.session_state['end_date']   = datetime.now().date()
                        st.rerun()

    # Renders the Plotly closing price chart for a single company or all companies
    def _render_chart(self, df_close, current_info):
        if df_close is None or df_close.empty:
            st.error("No data available to display.")
            return

        start = pd.Timestamp(st.session_state['start_date']).tz_localize(None)
        end   = pd.Timestamp(st.session_state['end_date']).tz_localize(None)
        if df_close.index.tz is not None:
            df_close.index = df_close.index.tz_localize(None)
        df_plot = df_close.loc[start:end]

        if df_plot.empty:
            st.warning("No data available for the selected date range.")
            return

        # Fix 4 — generate chart title from TICKERS keys rather than hard-coding company names
        chart_title = (
            ", ".join(TICKERS.keys())
            if self.selected_company == "All Companies"
            else self.selected_company
        )
        fig = go.Figure()

        if self.selected_company == "All Companies":
            # Multi-line chart — one per company
            for name, ticker in TICKERS.items():
                if ticker in df_plot.columns:
                    fig.add_trace(go.Scatter(
                        x=df_plot.index, y=df_plot[ticker],
                        name=name, mode='lines',
                        line=dict(color=BANK_COLOR_MAP[ticker], width=2.5)
                    ))

            fig.update_layout(
                title=f'Closing Price - {chart_title}  •  {current_info}',
                title_y=0.96, title_font=dict(size=22),
                yaxis_title='Closing Price (p)',
                margin=dict(t=80),
                xaxis=dict(title='Date', title_font=dict(weight='bold', size=14),
                           tickfont=dict(weight='bold'), zeroline=True,
                           zerolinecolor='lightgray', zerolinewidth=1),
                yaxis=dict(title_font=dict(weight='bold', size=14),
                           tickfont=dict(weight='bold'), zeroline=True,
                           zerolinecolor='lightgray', zerolinewidth=1),
                hovermode="x unified", height=670,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
        else:
            # Single-line chart — for the selected company
            ticker = TICKERS[self.selected_company]
            col    = ticker if ticker in df_plot.columns else 'Close'
            if col in df_plot.columns:
                fig.add_trace(go.Scatter(
                    x=df_plot.index, y=df_plot[col],
                    name=self.selected_company, mode='lines',
                    line=dict(color=BANK_COLOR_MAP[ticker], width=3)
                ))

            fig.update_layout(
                title=f'Historical Data - {chart_title}  •  {current_info}',
                title_y=0.96, title_font=dict(size=22),
                margin=dict(t=50),
                xaxis=dict(title='Date', title_font=dict(weight='bold', size=14),
                           tickfont=dict(weight='bold'), zeroline=True,
                           zerolinecolor='lightgray', zerolinewidth=1),
                yaxis=dict(title='Closing Price (p)', title_font=dict(weight='bold', size=14),
                           tickfont=dict(weight='bold'), zeroline=True,
                           zerolinecolor='lightgray', zerolinewidth=1),
                hovermode="x unified", height=670,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )

        st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

    # Renders a sortable historical OHLCV data table below the chart for a single company
    def _render_data_table(self):
        if self.selected_company == "All Companies":
            return
        try:
            ticker    = TICKERS[self.selected_company]
            start_str = st.session_state['start_date'].strftime('%Y-%m-%d')
            end_str   = st.session_state['end_date'].strftime('%Y-%m-%d')
            range_lbl = st.session_state.get('active_range', 'Custom')
            if range_lbl == 'Custom':
                range_lbl = f"{start_str} → {end_str}"

            df_range = StockDataService.get_stock_data([ticker], start_str, end_str)
            if df_range is None or df_range.empty:
                st.info("No data available for the selected period.")
                return

            st.markdown("---")
            st.markdown(
                f"<p style='font-size:16px;font-weight:bold;'>"
                f"Historical Daily Data – {self.selected_company} ({range_lbl})</p>",
                unsafe_allow_html=True
            )

            df_display = df_range.copy().dropna()
            if isinstance(df_display.columns, pd.MultiIndex):
                df_display.columns = df_display.columns.get_level_values(0)
            df_display = df_display.reset_index()
            df_display['Date'] = pd.to_datetime(df_display['Date'])

            desired_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
            df_display   = df_display[[c for c in desired_cols if c in df_display.columns]]
            df_display   = df_display.sort_values(by='Date', ascending=False)

            start_dt = pd.to_datetime(start_str)
            end_dt   = pd.to_datetime(end_str) + pd.Timedelta(days=1)
            df_display = df_display[
                (df_display['Date'] >= start_dt) & (df_display['Date'] < end_dt)
            ].copy()

            df_display['Date'] = df_display['Date'].dt.strftime('%Y-%m-%d')
            for col in ['Open', 'High', 'Low', 'Close', 'Adj Close']:
                if col in df_display.columns:
                    df_display[col] = df_display[col].apply(
                        lambda x: f'{x:,.2f}' if pd.notna(x) else ''
                    )

            st.dataframe(df_display, width='stretch')
            st.markdown("<br>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Could not load historical data table: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR & ROUTING
# ══════════════════════════════════════════════════════════════════════════════

# Page title — rendered at module level, outside the HomeScreen class
st.markdown(
    "<h1 style='text-align:center;margin-top:-60px;margin-bottom:40px;'>"
    "🏦 Stock Market Prediction - UK Banking Sector</h1>",
    unsafe_allow_html=True
)

# ── Sidebar: Company Selection ────────────────────────────────────────────────
st.sidebar.header("Data Options")

selected_company = st.sidebar.selectbox(
    "Select Company:",
    options=COMPANY_OPTIONS,
    key='selected_company'
)

# ── Sidebar: Date Inputs ──────────────────────────────────────────────────────
today = datetime.now().date()

custom_start = st.sidebar.date_input(
    "Start Date:",
    st.session_state['start_date'],
    max_value=today
)
custom_end = st.sidebar.date_input(
    "End Date:",
    st.session_state['end_date'],
    max_value=today
)

# Triggers a rerun if the user manually changes the date inputs in the sidebar
if (custom_start != st.session_state['start_date'] or
        custom_end != st.session_state['end_date']):
    st.session_state['start_date']   = custom_start
    st.session_state['end_date']     = custom_end
    st.session_state['active_range'] = None
    st.rerun()

# ── Sidebar: Info ─────────────────────────────────────────────────────────────
st.sidebar.markdown("---")

# ── Render ────────────────────────────────────────────────────────────────────
HomeScreen(st.session_state.get('selected_company', COMPANY_OPTIONS[0])).render()
