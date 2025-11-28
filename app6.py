import streamlit as st
import pandas as pd
import numpy as np
from math import log, sqrt, exp, pi

# ------------------------------------------------------------
# Normal CDF (Error function based, NO SCIPY NEEDED)
# ------------------------------------------------------------
def norm_cdf(x):
    """ Approximate CDF of standard normal distribution """
    return (1.0 + np.math.erf(x / np.sqrt(2.0))) / 2.0

# ------------------------------------------------------------
# FX OPTION PRICING (Garman–Kohlhagen) - NO SCIPY
# ------------------------------------------------------------
def fx_option_price(S, K, T, rd, rf, sigma, option_type="Call"):
    d1 = (log(S / K) + (rd - rf + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)

    if option_type == "Call":
        price = S * exp(-rf * T) * norm_cdf(d1) - K * exp(-rd * T) * norm_cdf(d2)
    else:
        price = K * exp(-rd * T) * norm_cdf(-d2) - S * exp(-rf * T) * norm_cdf(-d1)

    return price, d1, d2

# ------------------------------------------------------------
# STREAMLIT PAGE SETTINGS
# ------------------------------------------------------------
st.set_page_config(page_title="USDINR Forex Options", layout="wide")

st.title("💱 USD/INR Forex Options App")
st.write("Spot/Future, Option Chain, Option Calculator — **NO SCIPY REQUIRED**")

# Sidebar Inputs
st.sidebar.header("📌 Market Inputs")
spot = st.sidebar.number_input("Spot Price (USD/INR)", value=83.20)
future = st.sidebar.number_input("Future Price (USD/INR)", value=83.50)
vol = st.sidebar.number_input("Volatility (σ)", value=0.08)
rd = st.sidebar.number_input("Domestic Rate (India)", value=0.065)
rf = st.sidebar.number_input("Foreign Rate (US)", value=0.052)
exp_days = st.sidebar.number_input("Days to Expiry", value=30)

T = exp_days / 365

# Display Spot & Future
st.markdown(
    f"""
    ### 📌 Market Prices
    **Spot:** <span style='color:#00b300;font-size:22px;font-weight:bold'>{spot}</span>  
    **Future:** <span style='color:#0066ff;font-size:22px;font-weight:bold'>{future}</span>
    """,
    unsafe_allow_html=True
)

# ------------------------------------------------------------
# OPTION CHAIN
# ------------------------------------------------------------
st.subheader("📊 USD/INR Option Chain")

strikes = np.arange(spot - 2, spot + 3, 0.25)
atm_strike = min(strikes, key=lambda x: abs(x - spot))

chain = []
for K in strikes:
    call, _, _ = fx_option_price(spot, K, T, rd, rf, vol, "Call")
    put, _, _ = fx_option_price(spot, K, T, rd, rf, vol, "Put")

    if abs(K - atm_strike) < 0.01:
        status = "ATM"
    elif K < spot:
        status = "ITM"
    else:
        status = "OTM"

    chain.append([K, round(call, 4), round(put, 4), status])

df = pd.DataFrame(chain, columns=["Strike", "Call", "Put", "Status"])

# Color coding
def highlight(row):
    if row["Status"] == "ATM":
        return ["background-color:#fff2cc"] * 4
    elif row["Status"] == "ITM":
        return ["background-color:#d9ead3"] * 4
    else:
        return ["background-color:#f4cccc"] * 4

st.dataframe(df.style.apply(highlight, axis=1))

# ------------------------------------------------------------
# OPTION CALCULATOR
# ------------------------------------------------------------
st.subheader("🧮 Option Calculator")

col1, col2 = st.columns(2)

with col1:
    K = st.number_input("Strike Price", value=float(atm_strike))
    option_type = st.selectbox("Option Type", ["Call", "Put"])

with col2:
    sigma_calc = st.number_input("Volatility", value=vol)
    days_calc = st.number_input("Days to Expiry", value=exp_days)

T_calc = days_calc / 365

price, d1, d2 = fx_option_price(spot, K, T_calc, rd, rf, sigma_calc, option_type)

st.markdown(f"""
### 🟦 Option Price: **₹ {round(price, 4)}**

#### Greeks  
- d1: **{round(d1, 4)}**  
- d2: **{round(d2, 4)}**

""")

st.success("This version uses NO SCIPY. Safe to deploy on Streamlit Cloud.")

# ------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------
st.markdown("---")
st.markdown("### 🚀 Ready for deployment on share.streamlit.io")




