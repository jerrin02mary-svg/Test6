import streamlit as st
import pandas as pd
import numpy as np
from math import log, sqrt, exp
from scipy.stats import norm

# ------------------------------------------------------------
# FX OPTION CALCULATOR (Garman-Kohlhagen)
# ------------------------------------------------------------
def fx_option_price(S, K, T, rd, rf, sigma, option_type="Call"):
    d1 = (np.log(S / K) + (rd - rf + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == "Call":
        price = S * exp(-rf * T) * norm.cdf(d1) - K * exp(-rd * T) * norm.cdf(d2)
    else:
        price = K * exp(-rd * T) * norm.cdf(-d2) - S * exp(-rf * T) * norm.cdf(-d1)

    return price, d1, d2


# ------------------------------------------------------------
# STREAMLIT UI
# ------------------------------------------------------------
st.set_page_config(page_title="USDINR Forex Option Calculator", layout="wide")

st.title("💱 USD/INR Forex Options – Option Chain + Calculator")

# Sidebar
st.sidebar.header("📌 Market Inputs")
spot = st.sidebar.number_input("Spot Price (USD/INR)", value=83.20)
future = st.sidebar.number_input("Future Price (USD/INR)", value=83.50)
vol = st.sidebar.number_input("Volatility (σ)", value=0.08)
rd = st.sidebar.number_input("Domestic Interest Rate (India)", value=0.065)
rf = st.sidebar.number_input("Foreign Interest Rate (US)", value=0.052)
exp_days = st.sidebar.number_input("Days to Expiry", value=30)

T = exp_days / 365

st.markdown(
    f"""
    ### 📌 Spot & Future Price  
    - **Spot Price:** <span style='color:#00b300; font-size:22px; font-weight:bold;'>{spot}</span>  
    - **Future Price:** <span style='color:#0066ff; font-size:22px; font-weight:bold;'>{future}</span>  
    """,
    unsafe_allow_html=True
)

# ------------------------------------------------------------
# OPTION CHAIN GENERATION
# ------------------------------------------------------------
st.subheader("📊 USD/INR Option Chain")

strikes = np.arange(spot - 2, spot + 2.5, 0.25)
atm_strike = min(strikes, key=lambda x: abs(x - spot))

option_chain = []

for K in strikes:
    call, _, _ = fx_option_price(spot, K, T, rd, rf, vol, "Call")
    put, _, _ = fx_option_price(spot, K, T, rd, rf, vol, "Put")

    status = (
        "ATM" if abs(K - atm_strike) < 0.01
        else "ITM" if K < spot
        else "OTM"
    )

    option_chain.append([K, round(call, 4), round(put, 4), status])

df = pd.DataFrame(option_chain, columns=["Strike", "Call Price", "Put Price", "Status"])


# Apply colors
def color_status(row):
    if row["Status"] == "ATM":
        return ["background-color: #fff2cc"]*4
    elif row["Status"] == "ITM":
        return ["background-color: #d9ead3"]*4
    else:
        return ["background-color: #f4cccc"]*4

st.dataframe(df.style.apply(color_status, axis=1))

# ------------------------------------------------------------
# OPTION CALCULATOR
# ------------------------------------------------------------
st.subheader("🧮 Forex Option Calculator")

col1, col2 = st.columns(2)

with col1:
    K = st.number_input("Strike Price", value=atm_strike)
    option_type = st.selectbox("Option Type", ["Call", "Put"])

with col2:
    cal_vol = st.number_input("Volatility (σ)", value=vol)
    cal_days = st.number_input("Days to Expiry", value=exp_days)

cal_T = cal_days / 365

price, d1, d2 = fx_option_price(spot, K, cal_T, rd, rf, cal_vol, option_type)

st.markdown(f"""
### 🟦 Option Price: **₹ {round(price, 4)}**

#### Greeks  
- **d1:** {round(d1, 4)}  
- **d2:** {round(d2, 4)}  
""")

st.success("Calculator ready. You can now deploy this to share.streamlit.io!")

# ------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------
st.markdown("""
---
### 🚀 Deployment Instructions  
1. Create a GitHub repository  
2. Upload this file as **app.py**  
3. Visit **https://share.streamlit.io**  
4. Select your GitHub repo  
5. Deploy  

Enjoy your USD/INR FX Options App 🎯  
""")
