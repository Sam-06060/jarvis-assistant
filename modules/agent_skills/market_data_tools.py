import logging
from .base import AgentTool

logger = logging.getLogger(__name__)


class MarketDataTool(AgentTool):
    name = "get_market_data"
    description = (
        "Get live/current market prices and exchange rates using yfinance/Yahoo Finance. "
        "Use this FIRST for stocks, crypto, commodities, gold, silver, oil, forex, currency rates, "
        "and simple live price lookups. Never use run_command or scrape a page for these. "
        "Input: {'query': str}. Example: {'query': 'current gold price in USD'}"
    )
    permission = "safe"

    def run(self, inp: dict):
        query = inp.get("query", "").strip()
        if not query:
            return "Error: 'query' is required."

        try:
            from modules.live_data_service import LiveDataService
            result = LiveDataService.resolve_market_data(query)
            if result:
                return result
            return (
                "Error: Could not resolve a live market symbol for this query. "
                "Try a clearer ticker, commodity, crypto symbol, or currency pair."
            )
        except Exception as e:
            logger.error(f"MarketDataTool failed: {e}")
            return f"Error fetching live market data: {str(e)}"
