import re
import urllib.parse
import requests
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class LiveDataService:
    _MARKET_KEYWORDS = {
        "price", "rate", "stock", "share", "market", "crypto", "coin",
        "currency", "forex", "fx", "exchange", "quote", "gold", "silver",
        "oil", "bitcoin", "btc", "ethereum", "eth",
    }

    _COMMODITY_AND_CRYPTO_TICKERS = {
        "gold": "GC=F",
        "silver": "SI=F",
        "oil": "CL=F",
        "crude": "CL=F",
        "natural gas": "NG=F",
        "bitcoin": "BTC-USD",
        "btc": "BTC-USD",
        "ethereum": "ETH-USD",
        "eth": "ETH-USD",
    }

    _CURRENCY_CODES = {
        "usd", "inr", "eur", "gbp", "jpy", "aud", "cad", "chf", "cny",
        "sgd", "hkd", "aed", "sar", "nzd",
    }

    @classmethod
    def is_market_data_query(cls, query: str) -> bool:
        """Return True when a query is asking for a live quote/rate."""
        q = (query or "").lower()
        if not q.strip():
            return False
        if any(kw in q for kw in cls._MARKET_KEYWORDS):
            return True
        return bool(re.search(r"\b[A-Z]{1,5}(?:=[A-Z])?\b", query or ""))

    @staticmethod
    def resolve_market_data(query: str) -> str:
        """
        Interprets a query for live market data (stocks, crypto, commodities)
        and fetches strictly accurate live data using yfinance/Yahoo Finance.
        """
        q = (query or "").lower()
        if not LiveDataService.is_market_data_query(query):
            return None
            
        ticker = LiveDataService.resolve_ticker(query)
        
        if ticker:
            quote = LiveDataService._fetch_with_yfinance(ticker) or LiveDataService._fetch_with_yahoo_chart(ticker)
            if quote:
                return LiveDataService._format_quote(quote)
                
        return None

    @staticmethod
    def resolve_ticker(query: str) -> str:
        """Resolve a natural-language market query to a Yahoo Finance symbol."""
        q = (query or "").lower()

        # Specific commodity/crypto overrides avoid vague search hits.
        for name, symbol in LiveDataService._COMMODITY_AND_CRYPTO_TICKERS.items():
            if name in q:
                return symbol

        fx_symbol = LiveDataService._resolve_currency_pair(q)
        if fx_symbol:
            return fx_symbol

        explicit = re.search(r"\b([A-Z]{1,5}(?:=[A-Z])?)\b", query or "")
        if explicit:
            symbol = explicit.group(1)
            if symbol.upper() not in {"USD", "INR", "EUR", "GBP"}:
                return symbol

        # Dynamically resolve company name to ticker using Yahoo Search API.
        extract_company = re.sub(
            r"\b(what|is|the|live|current|latest|stock|price|rate|share|of|for|crypto|coin|quote|market|in|usd|please|tell|me|get|fetch|email|mail|send|scrape|internet)\b",
            " ",
            q,
        ).strip()
        extract_company = re.sub(r"\s+", " ", extract_company)
        if len(extract_company) > 1:
            url = f"https://query1.finance.yahoo.com/v1/finance/search?q={urllib.parse.quote(extract_company)}"
            headers = LiveDataService._headers()
            try:
                r = requests.get(url, headers=headers, timeout=3)
                if r.status_code == 200:
                    data = r.json()
                    for quote in data.get("quotes", []):
                        symbol = quote.get("symbol")
                        if symbol:
                            return symbol
            except Exception as e:
                logger.debug(f"[LiveDataService] Ticker search failed: {e}")

        return None

    @staticmethod
    def _resolve_currency_pair(q: str) -> str:
        compact = re.sub(r"[^a-z]", "", q)
        for base in LiveDataService._CURRENCY_CODES:
            for quote in LiveDataService._CURRENCY_CODES:
                if base == quote:
                    continue
                if f"{base}to{quote}" in compact or f"{base}{quote}" in compact:
                    return f"{base.upper()}{quote.upper()}=X"

        codes = re.findall(r"\b([a-z]{3})\b", q)
        codes = [c for c in codes if c in LiveDataService._CURRENCY_CODES]
        if len(codes) >= 2:
            return f"{codes[0].upper()}{codes[1].upper()}=X"
        return None

    @staticmethod
    def _fetch_with_yfinance(ticker: str) -> dict:
        """Use yfinance when it is installed; fall back silently otherwise."""
        try:
            import yfinance as yf
            data = yf.Ticker(ticker).fast_info
            price = getattr(data, "last_price", None) or data.get("last_price")
            currency = getattr(data, "currency", None) or data.get("currency") or "USD"
            if price is not None:
                return {
                    "symbol": ticker,
                    "price": price,
                    "currency": currency,
                    "source": "yfinance/Yahoo Finance",
                }
        except Exception as e:
            logger.debug(f"[LiveDataService] yfinance fetch failed for {ticker}: {e}")
        return {}

    @staticmethod
    def _fetch_with_yahoo_chart(ticker: str) -> dict:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(ticker)}"
        try:
            r = requests.get(url, headers=LiveDataService._headers(), timeout=4)
            if r.status_code == 200:
                data = r.json()
                result = data["chart"]["result"][0]
                meta = result["meta"]
                price = meta.get("regularMarketPrice")
                if price is not None:
                    return {
                        "symbol": meta.get("symbol", ticker),
                        "price": price,
                        "currency": meta.get("currency", "USD"),
                        "source": "Yahoo Finance chart API",
                    }
        except Exception as e:
            logger.debug(f"[LiveDataService] Yahoo chart fetch failed for {ticker}: {e}")
        return {}

    @staticmethod
    def _format_quote(quote: dict) -> str:
        price = quote.get("price")
        try:
            price_text = f"{float(price):,.4f}".rstrip("0").rstrip(".")
        except Exception:
            price_text = str(price)
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        return (
            f"Live Market Data: {quote.get('symbol')} is currently priced at "
            f"{price_text} {quote.get('currency', 'USD')}. "
            f"Source: {quote.get('source', 'Yahoo Finance')}. As of: {timestamp}."
        )

    @staticmethod
    def _headers() -> dict:
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
