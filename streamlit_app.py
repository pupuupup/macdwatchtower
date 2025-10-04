import streamlit as st
import yfinance as yf
import pandas as pd

# =========================
# Universe lists (official)
# =========================
SET50_TICKERS = [
    "ADVANC","AOT","AWC","BANPU","BBL","BCP","BDMS","BEM","BH","BJC","BTS",
    "CBG","CCET","COM7","CPALL","CPF","CPN","CRC","DELTA","EGCO","GPSC","GULF",
    "HMPRO","IVL","KBANK","KKP","KTB","KTC","LH","MINT","MTC","OR","OSP","PTT",
    "PTTEP","PTTGC","RATCH","SCB","SCC","SCGP","TCAP","TIDLOR","TISCO","TLI",
    "TOP","TRUE","TTB","TU","VGI","WHA"
]

SET100_TICKERS = [
    "AAV","ADVANC","AEONTS","AMATA","AOT","AP","AURA","AWC","BA","BAM","BANPU",
    "BBL","BCH","BCP","BCPG","BDMS","BEM","BGRIM","BH","BJC","BLA","BTG","BTS",
    "CBG","CCET","CENTEL","CHG","CK","COM7","CPALL","CPF","CPN","CRC","DELTA",
    "DOHOME","EA","EGCO","ERW","GLOBAL","GPSC","GULF","GUNKUL","HANA","HMPRO",
    "ICHI","IRPC","ITC","IVL","JAS","JMART","JMT","JTS","KBANK","KCE","KKP","KTB",
    "KTC","LH","M","MBK","MEGA","MINT","MOSHI","MTC","OR","OSP","PLANB","PR9","PRM",
    "PTT","PTTEP","PTTGC","QH","RATCH","RCL","SAWAD","SCB","SCC","SCGP","SIRI",
    "SISB","SJWD","SPALI","SPRC","STA","STGT","TASCO","TCAP","TFG","TIDLOR","TISCO",
    "TLI","TOA","TOP","TRUE","TTB","TU","VGI","WHA","WHAUP"
]

CRYPTO10 = ["BTC-USD","ETH-USD","BNB-USD","SOL-USD","XRP-USD","ADA-USD","DOGE-USD","AVAX-USD","TRX-USD","DOT-USD"]
FOREX = ["USDTHB=X","JPYTHB=X"]
COMMODITIES = ["GC=F","SI=F","CL=F","HG=F","NG=F"]
COMMODITY_NAMES = {
    "GC=F": "Gold",
    "SI=F": "Silver",
    "CL=F": "Crude Oil",
    "HG=F": "Copper",
    "NG=F": "Natural Gas"
}

def yahoo_symbol(sym):
    if sym in SET50_TICKERS or sym in SET100_TICKERS:
        return sym + ".BK"
    return sym

# =========================
# Data Functions
# =========================
def fetch_yahoo(symbol, interval="1d", period="6mo"):
    try:
        df = yf.download(symbol, interval=interval, period=period, progress=False, auto_adjust=False)
        if df is None or df.empty:
            return None
        return df[["Close"]]
    except Exception:
        return None

def macd_cross(df):
    if df is None or len(df) < 35:
        return "None"
    exp1 = df["Close"].ewm(span=12, adjust=False).mean()
    exp2 = df["Close"].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signals = []
    prev_val = float(macd.iloc[-3])
    last_val = float(macd.iloc[-2])
    if prev_val < 0 and last_val > 0:
        signals.append("CrossUp(1d ago)")
    elif prev_val > 0 and last_val < 0:
        signals.append("CrossDown(1d ago)")
    prev_val = float(macd.iloc[-2])
    last_val = float(macd.iloc[-1])
    if prev_val < 0 and last_val > 0:
        signals.append("CrossUp(today)")
    elif prev_val > 0 and last_val < 0:
        signals.append("CrossDown(today)")
    if not signals:
        return "None"
    return " | ".join(signals)

def relative_strength(sym_a, sym_b, interval="1d", period="6mo"):
    df_a = fetch_yahoo(sym_a, interval, period)
    df_b = fetch_yahoo(sym_b, interval, period)
    if df_a is None or df_b is None:
        return None
    df = pd.concat([df_a["Close"], df_b["Close"]], axis=1, join="inner")
    df.columns = ["A", "B"]
    rs_df = (df["A"] / df["B"]).to_frame(name="Close")
    return rs_df

# =========================
# Streamlit UI
# =========================
st.title("📊 MACD Watchtower by pupuupup")
st.markdown(
    """
    ⚠️ คำชี้แจง (Disclaimer)

    เครื่องมือนี้ MACD Watchtower by pupuupup ถูกสร้างขึ้นเพื่อวัตถุประสงค์ด้านการศึกษาและการวิจัยเท่านั้น
    ไม่ถือเป็นคำแนะนำทางการเงิน การลงทุน หรือสัญญาณการซื้อขาย แต่อย่างใด

    ผู้ใช้งานทุกคนต้องรับผิดชอบต่อการตัดสินใจในการซื้อขายและลงทุนของตนเองทั้งหมด
    ผู้พัฒนาไม่รับผิดชอบต่อความเสียหายทางการเงินใด ๆ ที่อาจเกิดขึ้นจากการใช้งานแอปพลิเคชันนี้
    โปรดศึกษาข้อมูลและวิเคราะห์ด้วยตนเองก่อนตัดสินใจลงทุนทุกครั้ง
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns([1,2,1])
with col2:
    groups = st.multiselect("Select Groups", [
        "SET50","SET100",
        "SET50 Relative Strength (SET50 as base)",
        "SET100 Relative Strength (SET50 as base)",
        "Crypto 10","Crypto 10 Relative Strength (BTC as base)","Crypto 10 Relative Strength (ETH as base)",
        "Forex Pair","Commodity","Commodity Relative Strength (Gold as base)"
    ], default=["SET50"])

    timeframe = st.selectbox("Timeframe", ["Daily","Weekly"], index=0)
    interval = "1d" if timeframe=="Daily" else "1wk"
    period = "6mo" if timeframe=="Daily" else "2y"

    # ✅ Always show custom input box (no need to select "Custom")
    cs = st.text_area("Custom Symbols (optional)", placeholder="e.g. AOT.BK, BDMS.BK, CPALL.BK, AAPL, BABA")
    custom_symbols = [s.strip().upper() for s in cs.split(",") if s.strip()] if cs else []

    run = st.button("▶ Run Scanner")

# =========================
# Run Scanner
# =========================
if run:
    results = {}

    if "SET50" in groups:
        data = []
        for s in SET50_TICKERS:
            df = fetch_yahoo(yahoo_symbol(s), interval, period)
            sig = macd_cross(df)
            data.append([s, sig])
        results["SET50"] = pd.DataFrame(data, columns=["Symbol","Signal"])

    if "SET100" in groups:
        data = []
        for s in SET100_TICKERS:
            df = fetch_yahoo(yahoo_symbol(s), interval, period)
            sig = macd_cross(df)
            data.append([s, sig])
        results["SET100"] = pd.DataFrame(data, columns=["Symbol","Signal"])

    if "SET50 Relative Strength (SET50 as base)" in groups:
        base = "TDEX.BK"
        data = []
        for s in SET50_TICKERS:
            rs = relative_strength(yahoo_symbol(s), base, interval, period)
            sig = macd_cross(rs)
            data.append([f"{s}/SET50", sig])
        results["SET50 RS"] = pd.DataFrame(data, columns=["Symbol","Signal"])

    if "SET100 Relative Strength (SET50 as base)" in groups:
        base = "TDEX.BK"
        data = []
        for s in SET100_TICKERS:
            rs = relative_strength(yahoo_symbol(s), base, interval, period)
            sig = macd_cross(rs)
            data.append([f"{s}/SET50", sig])
        results["SET100 RS"] = pd.DataFrame(data, columns=["Symbol","Signal"])

    if "Crypto 10" in groups:
        data = []
        for s in CRYPTO10:
            df = fetch_yahoo(s, interval, period)
            sig = macd_cross(df)
            data.append([s.replace("-USD",""), sig])
        results["Crypto 10"] = pd.DataFrame(data, columns=["Symbol","Signal"])

    if "Crypto 10 Relative Strength (BTC as base)" in groups:
        base = "BTC-USD"
        data = []
        for s in CRYPTO10:
            if s==base: continue
            rs = relative_strength(s, base, interval, period)
            sig = macd_cross(rs)
            data.append([f"{s.replace('-USD','')}/BTC", sig])
        results["Crypto RS (BTC)"] = pd.DataFrame(data, columns=["Symbol","Signal"])

    if "Crypto 10 Relative Strength (ETH as base)" in groups:
        base = "ETH-USD"
        data = []
        for s in CRYPTO10:
            if s==base: continue
            rs = relative_strength(s, base, interval, period)
            sig = macd_cross(rs)
            data.append([f"{s.replace('-USD','')}/ETH", sig])
        results["Crypto RS (ETH)"] = pd.DataFrame(data, columns=["Symbol","Signal"])

    if "Forex Pair" in groups:
        data = []
        for s in FOREX:
            df = fetch_yahoo(s, interval, period)
            sig = macd_cross(df)
            data.append([s.replace("=X",""), sig])
        results["Forex"] = pd.DataFrame(data, columns=["Symbol","Signal"])

    if "Commodity" in groups:
        data = []
        for s in COMMODITIES:
            df = fetch_yahoo(s, interval, period)
            sig = macd_cross(df)
            data.append([COMMODITY_NAMES[s], sig])
        results["Commodity"] = pd.DataFrame(data, columns=["Symbol","Signal"])

    if "Commodity Relative Strength (Gold as base)" in groups:
        base = "GC=F"
        data = []
        for s in COMMODITIES:
            if s==base: continue
            rs = relative_strength(s, base, interval, period)
            sig = macd_cross(rs)
            data.append([f"{COMMODITY_NAMES[s]}/GOLD", sig])
        results["Commodity RS (Gold)"] = pd.DataFrame(data, columns=["Symbol","Signal"])

    # ✅ Custom section runs only if user typed something
    if custom_symbols:
        data = []
        for s in custom_symbols:
            df = fetch_yahoo(s, interval, period)
            sig = macd_cross(df)
            data.append([s, sig])
        results["Custom"] = pd.DataFrame(data, columns=["Symbol","Signal"])

    # Display
    for section, df in results.items():
        st.subheader(section)
        def colorize(val):
            if str(val).startswith("CrossUp"):
                return "background-color: lightgreen; color: black;"
            if str(val).startswith("CrossDown"):
                return "background-color: salmon; color: black;"
            return "color: grey;"
        st.dataframe(df.style.applymap(colorize, subset=["Signal"]))

