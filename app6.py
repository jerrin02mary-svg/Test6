# app.py
import streamlit as st
import pandas as pd
import numpy as np
from math import log, sqrt, exp, erf, isfinite

# -------------------------
# Normal CDF (uses math.erf)
# -------------------------
def norm_cdf(x):
    """CDF of standard normal using math.erf (no scipy)."""
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))

# -------------------------
# Garman-Kohlhagen FX Option Price (no scipy)
# -------------------------
def fx_option_price(S, K, T, rd, rf, sigma, option_type="Call"):
    """
    S: spot
    K: strike
    T: time in years
    rd, rf: continuous interest rates (decimals, e.g. 0.06)
    sigma: volatility (decimal, e.g. 0.08)
    option_type: "Call" or "Put"
    """
    # handle degenerate cases
    if T <= 0 or sigma <= 0:
        # immediate expiry or zero vol -> intrinsic value discounted
        disc_dom = exp(-rd * T)
        disc_for = exp(-rf * T)
        if option_type == "Call":
            price = max(0.0, S * disc_for - K * disc_dom)
        else:
            price = max(0.0, K * disc_dom - S * disc_for)
        # return d1,d2 as None for degenerate case
        return price, None, None

    sqrtT = sqrt(T)
    d1 = (log(S / K) + (rd - rf + 0.5 * sigma * sigma) * T) / (sigma * sqrtT)
    d2 = d1 - sigma * sqrtT

    if option_type == "Call":
        price = S * exp(-rf * T) * norm_cdf(d1) - K * exp(-rd * T) * norm_cdf(d2)
    else:
        price = K * exp(-rd * T) * norm_cdf(-d2) - S * exp(-rf * T) * norm_cdf(-d1)

    return price, d1, d2

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="USD/INR FX Options", layout="wide")
st.title("💱 USD/INR Forex Options — No SciPy (fixed)")

# Sidebar inputs
st.sidebar.header("Market Inputs")
spot = st.sidebar.number_input("Spot Price (USD/INR)", value=83.20, format="%.4f")
future = st.sidebar.number_input("Future Price (USD/INR)", value=83.50, format="%.4f")
# Volatility as decimal e.g., 0.08 for 8% — keep UI label clear
vol = st.sidebar.number_input("Volatility (σ) — decimal (e.g. 0.08 = 8%)", value=0.08, format="%.6f")
rd = st.sidebar.number_input("Domestic Rate (rd) — decimal (e.g. 0.06)", value=0.065, format="%.6f")
rf = st.sidebar.number_input("Foreign Rate (rf) — decimal (e.g. 0.05)", value=0.052, format="%.6f")
exp_days = st.sidebar.number_input("Days to Expiry", min_value=0, value=30)

T = max(exp_days / 365.0, 0.0)

# Show spot & future with colors
st.markdown(
    f"""
    ### Market Prices
    - **Spot:** <span style='color:#008000; font-weight:700;'>{spot}</span>  
    - **Future:** <span style='color:#0057d9; font-weight:700;'>{future}</span>
    """,
    unsafe_allow_html=True,
)

# Option chain generation
st.subheader("USD/INR Option Chain (generated)")

# generate strikes around spot
step = 0.25
lower = spot - 2.0
upper = spot + 3.0
strikes = np.round(np.arange(lower, upper + 1e-9, step), 4)

# find nearest ATM strike
atm_strike = float(min(strikes, key=lambda x: abs(x - spot)))

rows = []
for K in strikes:
    price_call, _, _ = fx_option_price(spot, K, T, rd, rf, vol, "Call")
    price_put, _, _ = fx_option_price(spot, K, T, rd, rf, vol, "Put")

    if abs(K - atm_strike) <= 1e-6:
        status = "ATM"
    elif K < spot:
        status = "ITM"
    else:
        status = "OTM"

    rows.append({"Strike": K, "Call": round(price_call, 6), "Put": round(price_put, 6), "Status": status})

df = pd.DataFrame(rows)

# styling for ATM/ITM/OTM
def row_style(row):
    st = row["Status"]
    if st == "ATM":
        color = "background-color: #fff2cc"  # light yellow
    elif st == "ITM":
        color = "background-color: #d9ead3"  # light green
    else:
        color = "background-color: #f4cccc"  # light red
    return [color] * len(row)

st.dataframe(df.style.apply(row_style, axis=1), use_container_width=True)

# Option calculator
st.subheader("Option Calculator")

col1, col2 = st.columns(2)
with col1:
    K_input = st.number_input("Strike Price", value=atm_strike, format="%.4f")
    opt_type = st.selectbox("Option Type", ["Call", "Put"])
with col2:
    vol_input = st.number_input("Volatility (σ) — decimal", value=vol, format="%.6f")
    days_input = st.number_input("Days to expiry", min_value=0, value=exp_days)

T_calc = max(days_input / 365.0, 0.0)

price, d1, d2 = fx_option_price(spot, K_input, T_calc, rd, rf, vol_input, opt_type)

st.markdown(f"### Option Price: **₹ {round(price, 6)}**")
if d1 is None or d2 is None:
    st.info("Degenerate case (zero volatility or zero time). Greeks unavailable.")
else:
    st.markdown(f"- d1: `{round(d1,6)}`  \n- d2: `{round(d2,6)}`")

st.markdown("---")
st.markdown("This app uses `math.erf` for the normal CDF (no SciPy). Deployable on Streamlit Cloud.")

   



   
    



