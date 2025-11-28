# app.py
import streamlit as st
import pandas as pd
import numpy as np
from math import log, sqrt, exp, erf

# --------------------------------------------------------------------
# NORMAL CDF (NO SCIPY)
# --------------------------------------------------------------------
def norm_cdf(x):
    return 0.5 * (1.0 + erf(x / sqrt(2)))

# --------------------------------------------------------------------
# FX OPTION PRICING (Garman-Kohlhagen Model)
# --------------------------------------------------------------------
def fx_option_price(S, K, T, rd, rf, sigma, option_type="Call"):
    if T <= 0 or sigma <= 0:
        # intrinsic value (simplified)
        if option_type == "Call":
            return max(0, S - K), None, None
        else:
            return max(0, K - S), None, None

    sqrtT = sqrt(T)
    d1 = (log(S/K) + (rd - rf + 0.5*sigma*sigma)*T) / (sigma*sqrtT)
    d2 = d1 - sigma*sqrtT

    if option_type == "Call":
        price = S*exp(-rf*T)*norm_cdf(d1) - K*exp(-rd*T)*norm_cdf(d2)
    else:
        price = K*exp(-rd*T)*norm_cdf(-d2) - S*exp(-rf*T)*norm_cdf(-d1)

    return price, d1, d2

# --------------------------------------------------------------------
# STREAMLIT PAGE
# --------------------------------------------------------------------
st.set_page_config(page_title="USDINR FX Option Calculator", layout="wide")

st.title("💱 USD/INR Forex Options — ATM / ITM / OTM Breakdown")

# Sidebar Inputs
st.sidebar.header("Market Inputs")
spot = st.sidebar.number_input("Spot Price (USD/INR)", value=83.20)
future = st.sidebar.number_input("Future Price (USD/INR)", value=83.50)
vol = st.sidebar.number_input("Volatility (decimal, 0.08 = 8%)", value=0.08)
rd = st.sidebar.number_input("Domestic Rate (rd)", value=0.065)
rf = st.sidebar.number_input("Foreign Rate (rf)", value=0.052)
days = st.sidebar.number_input("Days to Expiry", value=30)

T = max(days / 365, 0)

# --------------------------------------------------------------------
# DISPLAY SPOT & FUTURE
# --------------------------------------------------------------------
st.markdown(
    f"""
    ### 📌 Market Prices  
    **Spot:** <span style='color:#008000;font-weight:bold'>{spot}</span>  
    **Future:** <span style='color:#0057d9;font-weight:bold'>{future}</span>
    """, unsafe_allow_html=True
)

# --------------------------------------------------------------------
# OPTION CHAIN GENERATION
# --------------------------------------------------------------------
st.subheader("📊 Option Chain (Auto-Generated)")

strike_list = np.round(np.arange(spot - 2, spot + 3, 0.25), 4)

atm_strike = float(min(strike_list, key=lambda x: abs(x - spot)))

rows = []
for K in strike_list:
    call, _, _ = fx_option_price(spot, K, T, rd, rf, vol, "Call")
    put, _, _ = fx_option_price(spot, K, T, rd, rf, vol, "Put")

    if abs(K - atm_strike) < 0.001:
        status = "ATM"
    elif K < spot:
        status = "ITM"
    else:
        status = "OTM"

    rows.append([K, round(call, 6), round(put, 6), status])

df = pd.DataFrame(rows, columns=["Strike", "Call", "Put", "Status"])

# --------------------------------------------------------------------
# SEPARATE TABLES: ITM / ATM / OTM
# --------------------------------------------------------------------
st.markdown("## 🎯 ATM Strike")
st.dataframe(df[df["Status"] == "ATM"], use_container_width=True)

st.markdown("## 🟩 In The Money (ITM)")
st.dataframe(df[df["Status"] == "ITM"], use_container_width=True)

st.markdown("## 🟥 Out of The Money (OTM)")
st.dataframe(df[df["Status"] == "OTM"], use_container_width=True)

# --------------------------------------------------------------------
# OPTION CALCULATOR
# --------------------------------------------------------------------
st.subheader("🧮 Option Calculator")

col1, col2 = st.columns(2)

with col1:
    K_input = st.number_input("Strike Price", value=atm_strike)
    type_input = st.selectbox("Option Type", ["Call", "Put"])

with col2:
    sigma_input = st.number_input("Volatility (decimal)", value=vol)
    days_input = st.number_input("Days to Expiry (for calculator)", value=days)

T_calc = max(days_input / 365, 0)

price, d1, d2 = fx_option_price(spot, K_input, T_calc, rd, rf, sigma_input, type_input)

st.markdown(f"### 💰 Option Price: **₹ {round(price, 6)}**")

if d1 is None:
    st.info("Zero volatility or expiry — Greeks unavailable.")
else:
    st.write(f"**d1:** {round(d1,6)}")
    st.write(f"**d2:** {round(d2,6)}")

st.markdown("---")
st.markdown("🚀 Fully compatible with Streamlit Cloud — SciPy removed.")


    





   



   
    



