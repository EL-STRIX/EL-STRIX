"""Production-ready GitHub API Client for REST and GraphQL."""

import time
import requests
from typing import Any, Dict, Optional, List, Union
from urllib.parse import urljoin

from env import EnvManager
from logger import logger
from exceptions import GitHubAPIError, RateLimitError
from cache_manager import CacheManager
from paths import PathManager
from utils.file_helpers import ensure_dir

class GitHubClient:
    """Robust client for GitHub REST and GraphQL APIs with retry, caching, and rate limit handling."""
    
    BASE_URL = "https://api.github.com"
    GRAPHQL_URL = "https://api.github.com/graphql"
    
    def __init__(self):
        self.token = EnvManager.get_github_token()
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        # TTL: 1 hour for standard cache
        self.cache = CacheManager(ttl_seconds=3600)
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.max_retries = 3

    def _wait_for_rate_limit(self, reset_timestamp: int) -> None:
        """Wait until the rate limit resets."""
        now = int(time.time())
        sleep_duration = max(reset_timestamp - now, 0) + 1  # Add 1s buffer
        logger.warning(f"Rate limit exceeded. Waiting for {sleep_duration} seconds...")
        time.sleep(sleep_duration)
        logger.info("Rate limit reset. Resuming requests.")

    def _handle_response(self, response: requests.Response) -> Any:
        """Handle response status codes and rate limiting."""
        # Check rate limits first
        remaining = int(response.headers.get("X-RateLimit-Remaining", 1))
        reset = int(response.headers.get("X-RateLimit-Reset", 0))
        
        if response.status_code == 403 and remaining == 0:
            self._wait_for_rate_limit(reset)
            raise RateLimitError("Rate limit hit, please retry.")
            
        if response.status_code == 403 and "retry-after" in response.headers:
            retry_after = int(response.headers["retry-after"])
            logger.warning(f"Secondary rate limit hit. Waiting for {retry_after} seconds...")
            time.sleep(retry_after)
            raise RateLimitError("Secondary rate limit hit, please retry.")
            
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            logger.error(f"HTTP Error: {response.status_code} - {response.text}")
            raise GitHubAPIError(f"GitHub API Error: {response.status_code} - {response.text}") from e
            
        if not response.content:
            return None
            
        try:
            return response.json()
        except requests.JSONDecodeError:
            raise GitHubAPIError("Failed to parse JSON response from GitHub")

    def rest_request(self, method: str, endpoint: str, params: Optional[Dict] = None, paginated: bool = False, use_cache: bool = True) -> Any:
        """Execute a REST API request with automatic retries, pagination, and caching."""
        if not endpoint.startswith("http"):
            url = urljoin(self.BASE_URL, endpoint)
        else:
            url = endpoint
            
        cache_key = f"rest_{method}_{endpoint.replace('/', '_')}_{str(params)}"
        if use_cache and method.upper() == "GET":
            cached = self.cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit for {endpoint}")
                return cached
                
        logger.debug(f"REST {method.upper()} {url}")
        
        results = []
        current_url = url
        current_params = params or {}
        
        # Paginate limit
        max_pages = 100
        pages_fetched = 0
        
        while current_url and pages_fetched < max_pages:
            for attempt in range(1, self.max_retries + 1):
                try:
                    response = self.session.request(
                        method=method.upper(),
                        url=current_url,
                        params=current_params if pages_fetched == 0 else None, # Params already in URL for next pages
                        timeout=15
                    )
                    data = self._handle_response(response)
                    
                    if paginated and isinstance(data, list):
                        results.extend(data)
                        # Check for next page in Link header
                        if "next" in response.links:
                            current_url = response.links["next"]["url"]
                        else:
                            current_url = None
                    else:
                        results = data
                        current_url = None
                        
                    break # Success, break retry loop
                    
                except RateLimitError:
                    if attempt == self.max_retries:
                        raise GitHubAPIError("Max retries exceeded due to rate limiting.")
                    continue
                except (requests.ConnectionError, requests.Timeout) as e:
                    logger.warning(f"Network error on attempt {attempt}/{self.max_retries}: {e}")
                    if attempt == self.max_retries:
                        raise GitHubAPIError(f"Network error: {e}")
                    time.sleep(2 ** attempt)
                    
            pages_fetched += 1
            
        if use_cache and method.upper() == "GET":
            self.cache.set(cache_key, results)
            
        return results

    def graphql_request(self, query: str, variables: Optional[Dict] = None, use_cache: bool = True) -> Dict[str, Any]:
        """Execute a GraphQL API query with caching and retries."""
        cache_key = f"graphql_{hash(query)}_{hash(str(variables))}"
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                logger.debug("Cache hit for GraphQL query")
                return cached
                
        logger.debug("Executing GraphQL query")
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
            
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.post(
                    self.GRAPHQL_URL,
                    json=payload,
                    timeout=15
                )
                data = self._handle_response(response)
                
                if "errors" in data:
                    logger.error(f"GraphQL Errors: {data['errors']}")
                    raise GitHubAPIError(f"GraphQL Error: {data['errors'][0].get('message', 'Unknown')}")
                    
                result = data.get("data", {})
                if use_cache:
                    self.cache.set(cache_key, result)
                return result
                
            except RateLimitError:
                if attempt == self.max_retries:
                    raise GitHubAPIError("Max retries exceeded due to rate limiting.")
                continue
            except (requests.ConnectionError, requests.Timeout) as e:
                logger.warning(f"Network error on attempt {attempt}/{self.max_retries}: {e}")
                if attempt == self.max_retries:
                    raise GitHubAPIError(f"Network error: {e}")
                time.sleep(2 ** attempt)
                
        raise GitHubAPIError("Unexpected error during GraphQL request")

    def download_avatar(self, url: str) -> PathManager.ASSET_IMAGE_DIR:
        """Download and cache the user's avatar image."""
        ensure_dir(PathManager.ASSET_IMAGE_DIR)
        save_path = PathManager.ASSET_IMAGE_DIR / "avatar.png"
        
        logger.info(f"Downloading avatar from {url}")
        try:
            response = requests.get(url, stream=True, timeout=15)
            response.raise_for_status()
            
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            logger.info("Avatar downloaded successfully.")
            return save_path
        except requests.RequestException as e:
            logger.error(f"Failed to download avatar: {e}")
            raise GitHubAPIError(f"Avatar download failed: {e}")
