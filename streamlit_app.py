import streamlit as st
import yfinance as yf
import pandas as pd

# ===== SYMBOL GROUPS =====
set50_tickers = [
    "ADVANC.BK","AOT.BK","BANPU.BK","BBL.BK","BDMS.BK","BEM.BK","BGRIM.BK","BH.BK",
    "CBG.BK","CPALL.BK","CPF.BK","CPN.BK","CRC.BK","DELTA.BK","EA.BK","EGCO.BK",
    "GLOBAL.BK","GPSC.BK","GULF.BK","HANA.BK","HMPRO.BK","INTUCH.BK","IRPC.BK",
    "IVL.BK","KBANK.BK","KTB.BK","KTC.BK","LH.BK","MINT.BK","OR.BK","OSP.BK",
    "PTT.BK","PTTEP.BK","PTTGC.BK","RATCH.BK","SAWAD.BK","SCB.BK","SCC.BK","SCGP.BK",
    "TISCO.BK","TOP.BK","TRUE.BK","TTB.BK","TU.BK","WHA.BK"
]

set100_tickers = [
    "AAV.BK","ADVANC.BK","AEONTS.BK","AMATA.BK","AOT.BK","AP.BK","AURA.BK","AWC.BK",
    "BA.BK","BAM.BK","BANPU.BK","BBL.BK","BCH.BK","BCP.BK","BCPG.BK","BDMS.BK",
    "BEM.BK","BGRIM.BK","BH.BK","BJC.BK","BLA.BK","BTG.BK","BTS.BK","CBG.BK",
    "CCET.BK","CENTEL.BK","CHG.BK","CK.BK","COM7.BK","CPALL.BK","CPF.BK","CPN.BK",
    "CRC.BK","DELTA.BK","DOHOME.BK","EA.BK","EGCO.BK","ERW.BK","GLOBAL.BK","GPSC.BK",
    "GULF.BK","GUNKUL.BK","HANA.BK","HMPRO.BK","ICHI.BK","IRPC.BK","ITC.BK","IVL.BK",
    "JAS.BK","JMART.BK","JMT.BK","JTS.BK","KBANK.BK","KCE.BK","KKP.BK","KTB.BK",
    "KTC.BK","LH.BK","M.BK","MBK.BK","MEGA.BK","MINT.BK","MOSHI.BK","MTC.BK",
    "OR.BK","OSP.BK","PLANB.BK","PR9.BK","PRM.BK","PTT.BK","PTTEP.BK","PTTGC.BK",
    "QH.BK","RATCH.BK","RCL.BK","SAWAD.BK","SCB.BK","SCC.BK","SCGP.BK","SIRI.BK",
    "SISB.BK","SJWD.BK","SPALI.BK","SPRC.BK","STA.BK","STGT.BK","TASCO.BK","TCAP.BK",
    "TFG.BK","TIDLOR.BK","TISCO.BK","TLI.BK","TOA.BK","TOP.BK","TRUE.BK","TTB.BK",
    "TU.BK","VGI.BK","WHA.BK","WHAUP.BK"
]

crypto_pairs = [
    "BTC-USD","ETH-USD","BNB-USD","SOL-USD","XRP-USD",
    "DOGE-USD","ADA-USD","AVAX-USD","LINK-USD","TRX-USD"
]

commodities = {
    "GC=F": "Gold",
    "SI=F": "Silver",
    "CL=F": "Crude Oil"
}

forex_pairs = ["USDTHB=X"]

# ===== HELPERS =====
def fetch_yahoo(symbol, interval="1d", period="6mo"):
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=False)
        if "Close" in df and not df.empty:
            return df[["Close"]]
        else:
            return None
    except Exception:
        return None

def macd_cross(df):
    if df is None or len(df) < 35:
        return "None"
    exp1 = df["Close"].ewm(span=12, adjust=False).mean()
    exp2 = df["Close"].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    prev_val = macd.iloc[-3].item()
    last_val = macd.iloc[-2].item()
    if prev_val < 0 and last_val > 0:
        return "CrossUp"
    elif prev_val > 0 and last_val < 0:
        return "CrossDown"
    else:
        return "None"

def relative_strength(sym_a, sym_b, interval="1d", period="6mo"):
    df_a = fetch_yahoo(sym_a, interval, period)
    df_b = fetch_yahoo(sym_b, interval, period)
    if df_a is None or df_b is None:
        return None
    df = pd.concat([df_a["Close"], df_b["Close"]], axis=1, join="inner")
    df.columns = ["A", "B"]
    df["RS"] = df["A"] / df["B"]
    return df[["RS"]]

# ===== STREAMLIT APP =====
st.title("📊 MACD Zero-Line Cross & Relative Strength Scanner")

# Group toggles
groups = {
    "SET50": st.checkbox("SET50", value=False),
    "SET100": st.checkbox("SET100", value=False),
    "SET50 RS": st.checkbox("SET50 Relative Strength", value=False),
    "SET100 RS": st.checkbox("SET100 Relative Strength", value=False),
    "Crypto": st.checkbox("Crypto 10", value=False),
    "Crypto RS BTC": st.checkbox("Crypto RS (BTC base)", value=False),
    "Crypto RS ETH": st.checkbox("Crypto RS (ETH base)", value=False),
    "Forex": st.checkbox("Forex Pair", value=False),
    "Commodity": st.checkbox("Commodity", value=False),
    "Commodity RS": st.checkbox("Commodity RS (Gold base)", value=False),
}

# Custom list
custom_symbols = st.text_area("Custom Symbols (comma-separated, e.g. SISB.BK,NETBAY.BK)", "")
if custom_symbols:
    custom_list = [s.strip() for s in custom_symbols.split(",")]
else:
    custom_list = []

# Timeframe choice
timeframe = st.radio("Timeframe", ["Daily", "Weekly"], index=0)

if st.button("▶ Run Scanner"):
    st.write("### Results")

    interval = "1d" if timeframe == "Daily" else "1wk"
    period = "6mo" if timeframe == "Daily" else "2y"

    results = []

    # Example: SET50
    if groups["SET50"]:
        for s in set50_tickers:
            df = fetch_yahoo(s, interval, period)
            status = macd_cross(df)
            results.append([s, status])

    if groups["SET100"]:
        for s in set100_tickers:
            df = fetch_yahoo(s, interval, period)
            status = macd_cross(df)
            results.append([s, status])

    if custom_list:
        for s in custom_list:
            df = fetch_yahoo(s, interval, period)
            status = macd_cross(df)
            results.append([s, status])

    if groups["Crypto"]:
        for s in crypto_pairs:
            df = fetch_yahoo(s, interval, period)
            status = macd_cross(df)
            results.append([s, status])

    if groups["Commodity"]:
        for s, name in commodities.items():
            df = fetch_yahoo(s, interval, period)
            status = macd_cross(df)
            results.append([name, status])

    if groups["Forex"]:
        for s in forex_pairs:
            df = fetch_yahoo(s, interval, period)
            status = macd_cross(df)
            results.append([s, status])

    st.dataframe(pd.DataFrame(results, columns=["Symbol", "MACD Status"]))

