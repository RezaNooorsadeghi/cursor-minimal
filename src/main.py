from __future__ import annotations
import os, json
from datetime import datetime
from loguru import logger

def get_pair_symbol(default="EURUSD") -> str:
    return os.getenv("PAIR", default)

def fetch_quote(pair: str) -> dict:
    """
    Returns: {"source": "...", "pair": pair, "last": float, "ts": str}
    Tries OpenBB first (several import styles), falls back to yfinance.
    """
    # Try OpenBB (newer style)
    try:
        from openbb_core.app import OpenBB  # type: ignore
        r = OpenBB.forex.price.latest(symbol=pair)
        df = r.to_dataframe()
        last = float(df["close"].dropna().iloc[-1])
        ts = str(df["date"].iloc[-1])
        return {"source": "openbb-core", "pair": pair, "last": last, "ts": ts}
    except Exception:
        pass

    # Try OpenBB (older style)
    try:
        from openbb import obb  # type: ignore
        res = obb.forex.price.latest(symbol=pair)
        df = res.to_dataframe() if hasattr(res, "to_dataframe") else res
        last = float(df["close"].dropna().iloc[-1])
        ts = str(df["date"].iloc[-1])
        return {"source": "openbb", "pair": pair, "last": last, "ts": ts}
    except Exception:
        pass

    # Fallback to yfinance
    import yfinance as yf
    ticker = pair if pair.endswith("=X") else f"{pair}=X"
    df = yf.download(ticker, period="1d", interval="1m", progress=False)
    last = float(df["Close"].dropna().iloc[-1])
    ts = str(df.index[-1].to_pydatetime() if hasattr(df.index[-1], "to_pydatetime") else df.index[-1])
    return {"source": "yfinance", "pair": pair, "last": last, "ts": last}

def main() -> None:
    pair = get_pair_symbol()
    try:
        data = fetch_quote(pair)
        logger.info(f"Source={data['source']} Pair={data['pair']} Last={data['last']} @ {data['ts']}")
        print(json.dumps(data, indent=2))
    except Exception as e:
        logger.exception(f"Failed to fetch quote for {pair}: {e}")
        raise

if __name__ == "__main__":
    main()
