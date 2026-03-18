"""MCC classification service using OpenAI-compatible LLM."""

import asyncio
import json
import os
import re
from typing import List

import httpx
from openai import OpenAI

from ..data.mcc_codes import MCC_CODES, format_for_prompt
from ..domains.mcc import MCCResult, ScrapedData
from ..tools.scraper import scrape_urls

_SYSTEM_PROMPT = (
    "You are an expert in merchant classification for payment networks. "
    "You must classify merchants using NPCI MCC codes from ISO 18245. "
    "Always respond with valid JSON only. No prose before or after the JSON."
)

_USER_PROMPT_TEMPLATE = """\
Classify this merchant based on the following scraped website data:

URL: {url}
Page Title: {title}
Meta Description: {meta_description}
Keywords: {meta_keywords}
H1 Tags: {h1_tags}
H2 Tags: {h2_tags}
About Page Content: {about_content}

Choose the single best matching MCC from this list:
{mcc_list}

Respond ONLY with this JSON (no markdown, no code block):
{{
  "merchant_name": "<inferred merchant name>",
  "mcc_code": "<4-digit code>",
  "category": "<category name>",
  "confidence": "High|Medium|Low",
  "reasoning": "<one sentence explaining the choice>"
}}
"""


class MCCService:
    """Orchestrates scraping and LLM-based MCC classification."""

    def __init__(self) -> None:
        self._client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
            base_url=os.environ.get("OPENAI_BASE_URL"),
            http_client=httpx.Client(verify=False),
        )
        self._model = os.environ.get("LLM_MODEL", "gpt-4o")
        self._mcc_list = format_for_prompt()

    async def classify(self, urls: List[str]) -> List[MCCResult]:
        """Scrape URLs then classify each one with the LLM."""
        scraped_list = await scrape_urls(urls)
        results = []
        for data in scraped_list:
            result = await asyncio.to_thread(self._classify_one, data)
            results.append(result)
        return results

    def _classify_one(self, data: ScrapedData) -> MCCResult:
        """Call LLM to classify a single scraped merchant."""
        scrape_note = (
            f"(Note: website blocked scraping — classify using domain name only)"
            if data.error
            else ""
        )
        prompt = _USER_PROMPT_TEMPLATE.format(
            url=data.url + (" " + scrape_note if scrape_note else ""),
            title=data.title or "N/A",
            meta_description=data.meta_description or "N/A",
            meta_keywords=data.meta_keywords or "N/A",
            h1_tags=", ".join(data.h1_tags) if data.h1_tags else "N/A",
            h2_tags=", ".join(data.h2_tags) if data.h2_tags else "N/A",
            about_content=(data.about_content or "N/A")[:1000],
            mcc_list=self._mcc_list,
        )
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                max_tokens=512,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )
            raw = response.choices[0].message.content or ""
            parsed = self._parse_json(raw)
            mcc_code = parsed.get("mcc_code", "")
            mcc_info = MCC_CODES.get(mcc_code, {})
            return MCCResult(
                url=data.url,
                merchant_name=parsed.get("merchant_name"),
                mcc_code=mcc_code,
                category=parsed.get("category") or mcc_info.get("category"),
                confidence=parsed.get("confidence"),
                description=parsed.get("reasoning") or mcc_info.get("description"),
            )
        except Exception as exc:  # noqa: BLE001
            return MCCResult(url=data.url, error=f"Classification failed: {exc}")

    @staticmethod
    def _parse_json(text: str) -> dict:
        """Try to parse JSON from LLM response, with fallback regex extraction."""
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise
