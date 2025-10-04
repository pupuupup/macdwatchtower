import yfinance as yf
import pandas as pd

# ===== SYMBOL GROUPS =====
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

custom_list = ["SISB.BK","NETBAY.BK","SAPPE.BK"]

crypto_pairs = [
    "BTC-USD","ETH-USD","BNB-USD","SOL-USD","XRP-USD",
    "DOGE-USD","ADA-USD","AVAX-USD","LINK-USD","TRX-USD"
]

commodities = {
    "GC=F": "Gold (Weekly)",
    "SI=F": "Silver (Weekly)",
    "CL=F": "Crude Oil (Weekly)"
}

forex_pairs = [
    "USDTHB=X"
]


# ===== COLORS =====
RED = "\033[91m"
GREEN = "\033[92m"
GREY = "\033[90m"
RESET = "\033[0m"

# ===== HELPERS =====
def fetch_yahoo(symbol, interval="1d", period="6mo"):
    try:
        df = yf.download(
            symbol,
            period=period,
            interval=interval,
            progress=False,
            auto_adjust=False
        )
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

def print_status(symbol, status, is_weekly=False):
    label = f"[{symbol}]"
    if is_weekly:
        label += " (W)"

    if status == "CrossUp":
        print(f"{GREEN}{label} | {status}{RESET}")
    elif status == "CrossDown":
        print(f"{RED}{label} | {status}{RESET}")
    else:
        print(f"{GREY}{label} | None{RESET}")

def relative_strength(sym_a, sym_b, interval="1d", period="6mo"):
    df_a = fetch_yahoo(sym_a, interval, period)
    df_b = fetch_yahoo(sym_b, interval, period)
    if df_a is None or df_b is None:
        return None
    df = pd.concat([df_a["Close"], df_b["Close"]], axis=1, join="inner")
    df.columns = ["A", "B"]
    df["RS"] = df["A"] / df["B"]
    return df[["RS"]]

# ===== MAIN =====
print("=== MACD Zero-Line Cross Scanner ===")

# SET100 + Custom
for s in set100_tickers + custom_list:
    df = fetch_yahoo(s, "1d", "6mo")
    status = macd_cross(df)
    print_status(s, status)

# Crypto (Daily)
for s in crypto_pairs:
    df = fetch_yahoo(s, "1d", "6mo")
    status = macd_cross(df)
    print_status(s, status)

# Commodities (Daily)
for s, name in commodities.items():
    df = fetch_yahoo(s, interval="1d", period="6mo")
    status = macd_cross(df)
    print_status(s, status)

# Forex Pairs (Daily)
for s in forex_pairs:
    df = fetch_yahoo(s, "1d", "6mo")
    status = macd_cross(df)
    print_status(s, status)

# ===== Relative Strength =====
print("\n=== Relative Strength Cross Scanner ===")

#หุ้นไทย / SET100 proxy (ใช้ TDEX.BK แทน)
for s in set100_tickers:
    rs_df = relative_strength(s, "TDEX.BK")
    if rs_df is not None:
        status = macd_cross(rs_df.rename(columns={"RS": "Close"}))
        print_status(f"{s}/SET50", status)

# Extra ratios
pairs = [
    ("EEM", "URTH"),
    ("TDEX.BK", "EEM"),
    ("TDEX.BK", "URTH"),
    ("GC=F", "CL=F"),
    ("LINK-USD", "ETH-USD"),
    ("ETH-USD", "BTC-USD")
]

for a, b in pairs:
    rs_df = relative_strength(a, b)
    if rs_df is not None:
        status = macd_cross(rs_df.rename(columns={"RS": "Close"}))
        print_status(f"{a}/{b}", status)

