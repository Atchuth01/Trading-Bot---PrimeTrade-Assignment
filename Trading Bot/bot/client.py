
import hashlib
import hmac
import logging
import time
from urllib.parse import urlencode

import requests

logger = logging.getLogger("trading_bot.client")

DEFAULT_BASE_URL = "https://testnet.binancefuture.com"


class BinanceAPIError(Exception):
    

    def __init__(self, status_code, payload):
        self.status_code = status_code
        self.payload = payload
        super().__init__(f"Binance API error {status_code}: {payload}")


def _redact(params: dict) -> dict:
    
    redacted = dict(params)
    if "signature" in redacted:
        redacted["signature"] = "***"
    return redacted


class BinanceFuturesClient:
    def __init__(self, api_key: str, api_secret: str,
                 base_url: str = DEFAULT_BASE_URL, timeout: int = 10):
        if not api_key or not api_secret:
            raise ValueError("api_key and api_secret are required")

        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})

    def _sign(self, params: dict) -> dict:
        signed = dict(params)
        signed["timestamp"] = int(time.time() * 1000)
    
        signed.setdefault("recvWindow", 60000)
        query = urlencode(signed, doseq=True)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        signed["signature"] = signature
        return signed

    def _request(self, method: str, path: str, params: dict = None,
                 signed: bool = False) -> dict:
        url = f"{self.base_url}{path}"
        params = params or {}
        if signed:
            params = self._sign(params)

        logger.info("REQUEST  %s %s params=%s", method, path, _redact(params))

        try:
            response = self.session.request(
                method, url, params=params, timeout=self.timeout
            )
        except requests.exceptions.RequestException as exc:
            logger.error("NETWORK ERROR %s %s: %s", method, path, exc)
            raise

        try:
            payload = response.json()
        except ValueError:
            payload = {"raw": response.text}

        if not response.ok:
            logger.error(
                "RESPONSE ERROR %s %s status=%s body=%s",
                method, path, response.status_code, payload,
            )
            raise BinanceAPIError(response.status_code, payload)

        logger.info(
            "RESPONSE OK %s %s status=%s body=%s",
            method, path, response.status_code, payload,
        )
        return payload

    # -- endpoints used by this app -----------------------------------
    def new_order(self, **params) -> dict:
        
        return self._request("POST", "/fapi/v1/order", params=params, signed=True)

    def new_algo_order(self, **params) -> dict:
    
        return self._request("POST", "/fapi/v1/algoOrder", params=params, signed=True)

    def get_account(self) -> dict:
        
        return self._request("GET", "/fapi/v2/account", signed=True)

    def ping(self) -> dict:
        
        return self._request("GET", "/fapi/v1/ping")
