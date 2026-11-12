"""Minimal OpenAlex client.

The key is read from the OPENALEX_KEY environment variable and sent only in the
Authorization header, never in the URL. Every response updates the remaining
daily credit budget (X-RateLimit-Remaining), so callers can stop before it runs out.

Costs measured on 2026-11-10: a filter/group_by request = 1 credit,
a request with a `search` parameter = 10 credits. Daily limit 10 000.
"""
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://api.openalex.org"


class BudgetExhausted(Exception):
    pass


class OpenAlex:
    def __init__(self, key=None, floor=300, max_credits=None):
        # strip spaces, quotes and newlines that come along when the key is pasted
        self.key = (key or os.environ.get("OPENALEX_KEY") or "").strip().strip("\"'").strip()
        if not self.key:
            raise SystemExit("OPENALEX_KEY is not set")
        self.floor = floor              # stop when the server says fewer credits remain
        self.max_credits = max_credits  # optional cap for this run
        self.remaining = None
        self.spent = 0

    def _check(self):
        if self.remaining is not None and self.remaining < self.floor:
            raise BudgetExhausted(f"remaining={self.remaining}")
        if self.max_credits is not None and self.spent >= self.max_credits:
            raise BudgetExhausted(f"spent={self.spent}")

    def get(self, path, params, allow_search=False):
        """allow_search=True only for one-off runs with their own credit cap:
        a text search costs 10 credits per request."""
        self._check()
        is_search = any(k.startswith("search") for k in params) or ".search" in str(params.get("filter", ""))
        if is_search and not allow_search:
            raise ValueError("search costs 10 credits; filter locally instead")
        url = BASE + path + "?" + urllib.parse.urlencode(params, safe=":,|")
        req = urllib.request.Request(url, headers={
            "Authorization": "Bearer " + self.key,
            "User-Agent": "mashina (research; github.com/anuspenis/mashina1)",
        })
        for attempt in range(6):
            try:
                with urllib.request.urlopen(req, timeout=90) as r:
                    rem = r.headers.get("X-RateLimit-Remaining")
                    used = r.headers.get("X-RateLimit-Credits-Used")
                    if rem is not None:
                        self.remaining = int(rem)
                    self.spent += int(used) if used else 1
                    return json.load(r)
            except urllib.error.HTTPError as e:
                if e.code == 429 or e.code >= 500:
                    time.sleep(2 * (attempt + 1))
                    continue
                raise
            except (urllib.error.URLError, TimeoutError):
                time.sleep(2 * (attempt + 1))
        raise RuntimeError("OpenAlex request failed after retries: " + path)

    def year_counts(self, filt):
        """{year: count} for works matching the filter, 1950-2018."""
        j = self.get("/works", {"filter": filt + ",publication_year:1950-2018",
                                "group_by": "publication_year"})
        return {g["key"]: g["count"] for g in j["group_by"] if g["count"]}

    def count(self, filt):
        j = self.get("/works", {"filter": filt + ",publication_year:1950-2018", "per-page": 1})
        return j["meta"]["count"]
