from src.main import fetch_quote

def test_fetch_quote_returns_shape():
    d = fetch_quote("EURUSD")
    assert {"source","pair","last","ts"}.issubset(d.keys())
    assert d["pair"] == "EURUSD"
