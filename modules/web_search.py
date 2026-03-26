import traceback
import logging

logger = logging.getLogger(__name__)

# Try importing search libraries, handling potential missing dependencies gracefully
try:
    from ddgs import DDGS
except ImportError:
    DDGS = None

try:
    from googlesearch import search as google_search
except ImportError:
    google_search = None

try:
    import wikipedia
except ImportError:
    wikipedia = None

import requests
from bs4 import BeautifulSoup

class WebSearch:
    def __init__(self):
        """Initialize Search Engines"""
        self.ddgs = DDGS() if DDGS else None
        
        if not any([DDGS, google_search, wikipedia]):
            logger.warning("⚠️ No web search libraries found! Web search will not work.")

    def search(self, query, max_results=5):
        """
        Robust search with fallback: DDG -> Google -> Manual Scraper -> Wikipedia
        Returns a formatted string context.
        """
        # Clean conversational fluff from the query to improve search accuracy
        fluff_phrases = [
            "do you know ", "do you have information about ", "can you tell me ",
            "tell me ", "find out ", "search for ", "what is the ", "who is the "
        ]
        clean_query = query.lower()
        for fluff in fluff_phrases:
            if clean_query.startswith(fluff):
                clean_query = clean_query[len(fluff):].strip()
        # If we stripped everything, revert to the original query
        if len(clean_query) < 2:
            clean_query = query

        results = []
        source_used = "None"
        
        # 1. Try DuckDuckGo (Primary)
        if self.ddgs:
            logger.info(f"🔍 Searching DuckDuckGo: '{clean_query}'")
            try:
                # Fetch more results to allow filtering
                ddg_results = self.ddgs.text(clean_query, max_results=max_results + 3)
                
                if ddg_results:
                    filtered_count = 0
                    for res in ddg_results:
                        if filtered_count >= max_results: break
                        
                        title = res.get('title', 'No Title')
                        url = res.get('href', '#')
                        body = res.get('body', '')
                        if not body: body = res.get('snippet', '')
                        
                        # QUALITY FILTER
                        if len(body) < 40: continue # Skip empty/short snippets
                        if "login" in title.lower() or "sign up" in title.lower(): continue # Skip generic pages
                        
                        results.append(f"Title: {title}\nURL: {url}\nSummary: {body}")
                        filtered_count += 1
                        
                    source_used = "DuckDuckGo"
                else:
                    logger.info("⚠️ DuckDuckGo returned no results.")
            except Exception as e:
                logger.error(f"⚠️ DuckDuckGo failed: {e}")
        
        # 2. Try Google (Fallback 1)
        if not results and google_search:
            logger.info(f"🔍 Switch to Google Search: '{clean_query}'")
            try:
                # Try simple iterator
                g_results = list(google_search(clean_query, num_results=max_results, advanced=True))
                if g_results:
                    for res in g_results:
                         results.append(f"Title: {res.title}\nURL: {res.url}\nSummary: {res.description}")
                    source_used = "Google"
                else:
                    logger.info("⚠️ Google Search returned no results.")
            except Exception as e:
                logger.error(f"⚠️ Google Search failed: {e}")
                # Fallback to simple URL fetch if needed? No, without summary it's useless for LLM.

        # 3. Manual Fallback (Scraper) - If libs fail, try direct request
        if not results:
            try:
                logger.info(f"🔍 Switch to Manual Scraper (DuckDuckGo HTML)...")
                import requests
                from bs4 import BeautifulSoup
                
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
                }
                # Use DDG HTML endpoint directly
                url = f"https://html.duckduckgo.com/html/?q={clean_query}"
                resp = requests.get(url, headers=headers, timeout=5)
                
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    # DDG HTML Structure: .result -> .result__title -> a (link), .result__snippet (body)
                    for result in soup.select('.result')[:max_results]:
                        title_tag = result.select_one('.result__title a')
                        snippet_tag = result.select_one('.result__snippet')
                        
                        if title_tag and snippet_tag:
                            title = title_tag.get_text(strip=True)
                            link = title_tag['href']
                            snippet = snippet_tag.get_text(strip=True)
                            results.append(f"Title: {title}\nURL: {link}\nSummary: {snippet}")
                    
                    if results:
                        source_used = "Manual Scraper (DDG)"
                    else:
                        logger.warning("⚠️ Manual Scraper found no parsing matches.")
                else:
                    logger.warning(f"⚠️ Manual Request failed: {resp.status_code}")
            except Exception as e:
                logger.error(f"⚠️ Manual Scraper failed: {e}")

        # 4. Try Wikipedia (Last Resort)
        if not results and wikipedia:
            try:
                # Cleanup query for better Wiki matches
                # Don't strip "current" - it helps find incumbent/list pages
                clean_wiki_query = clean_query.replace("the", "").strip()
                if len(clean_wiki_query) < 4: clean_wiki_query = clean_query # Revert if too short
                
                logger.info(f"🔍 Switch to Wikipedia: '{clean_wiki_query}'")
                wiki_res = wikipedia.search(clean_wiki_query)
                
                if wiki_res:
                    # Fetch top 2 results
                    top_matches = wiki_res[:2]
                    for match in top_matches:
                        try:
                            # Verify relevance: Skip "Office" pages if looking for people? (Hard to generalize)
                            page_content = wikipedia.summary(match, sentences=4)
                            results.append(f"Source: Wikipedia ({match})\nSummary: {page_content}")
                        except: continue
                    
                    if results:
                        source_used = "Wikipedia"
                    else:
                         logger.info("⚠️ Wikipedia extraction failed for candidates.")
                else:
                    logger.info("⚠️ Wikipedia search returned no results.")
            except Exception as e:
                logger.error(f"⚠️ Wikipedia failed: {e}")

        return self._format_results(results, source_used)

    def fetch_url(self, url):
        """Fetches and extracts main text content from a URL. Uses Jina Reader for paywalls."""
        if not url.startswith("http"):
            return "Error: Invalid URL format. Must start with http/https."
            
        try:
            # Jina Reader Optimization: Add prefix for known "hard" sites or on failure
            hard_sites = ["genius.com", "azlyrics.com", "musixmatch.com", "lyrics.com", "songlyrics.com"]
            if any(site in url.lower() for site in hard_sites) and not url.startswith("https://r.jina.ai/"):
                logger.info(f"🔗 Using Jina Reader for restricted site: {url}")
                url = f"https://r.jina.ai/{url}"

            logger.info(f"📥 Fetching content from: {url}")
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
            }
            resp = requests.get(url, headers=headers, timeout=10)
            
            # Auto-fallback to Jina if standard fetch is blocked (403, 401, etc)
            if resp.status_code in [403, 401, 429] and not url.startswith("https://r.jina.ai/"):
                logger.info(f"🔄 Blocked ({resp.status_code}). Retrying via Jina Reader...")
                jina_url = f"https://r.jina.ai/{url}"
                resp = requests.get(jina_url, headers=headers, timeout=12)

            if resp.status_code != 200:
                return f"Error: Received status code {resp.status_code} from {url}"
                
            # If using Jina, it returns clean markdown already
            if "r.jina.ai" in url:
                content = resp.text
                # Clean Jina Markdown (strip header/footer metadata)
                content = re.sub(r"^Title:.*?\nURL Source:.*?\n\n", "", content, flags=re.DOTALL)
                content = re.sub(r"\[Markdown\]\(https://r.jina.ai/.*?\)$", "", content, flags=re.DOTALL)
                
                # Specialized header for lyrics to help Agent detect success
                if any(kw in content.lower() for kw in ["chorus", "verse", "[lyrics]", "lyrics:"]):
                    content = "--- LYRICS DETECTED (USE THIS DATA) ---\n" + content
                    
                # Genius specific cleaning: Strip everything before "Lyrics"
                if "genius.com" in url.lower() and "Lyrics" in content:
                    content = content[content.find("Lyrics"):]
            else:
                soup = BeautifulSoup(resp.text, 'html.parser')
                # Remove noise
                for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                    element.decompose()
                
                # Extract text
                text_tags = soup.find_all(['p', 'h1', 'h2', 'h3', 'article'])
                lines = [t.get_text(strip=True) for t in text_tags if len(t.get_text(strip=True)) > 20]
                content = "\n\n".join(lines)
                if len(content) < 100:
                    content = soup.get_text(separator="\n\n", strip=True)
            
            # Truncate thoughtfully (6000 chars ~ 1500 words is safe for all LLMs)
            limit = 6000
            if len(content) > limit:
                return content[:limit] + f"\n\n... (content truncated for brevity)"
            return content if content.strip() else "Error: No meaningful content found on the page."
            
        except Exception as e:
            return f"Error fetching {url}: {str(e)}"

    def _format_results(self, results, source_used):
        if not results:
            logger.info("❌ No search results found across all providers.")
            return ""

        logger.info(f"✅ Found results via {source_used}")
        formatted_context = f"--- WEB SEARCH RESULTS ({source_used}) ---\n"
        formatted_context += "\n\n".join(results)
        formatted_context += "\n-------------------------------------"
        return formatted_context

if __name__ == "__main__":
    # Test
    ws = WebSearch()
    print(ws.search("who is the current prime minister of india"))
