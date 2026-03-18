"""MCC domain models."""

from typing import List, Optional

from pydantic import BaseModel


class MCCClassifyRequest(BaseModel):
    """Request to classify a single merchant URL."""

    url: str


class MCCBatchRequest(BaseModel):
    """Request to classify multiple merchant URLs."""

    urls: List[str]


class ScrapedData(BaseModel):
    """Scraped data from a merchant website."""

    url: str
    title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    h1_tags: List[str] = []
    h2_tags: List[str] = []
    about_content: Optional[str] = None
    error: Optional[str] = None


class MCCResult(BaseModel):
    """MCC classification result for a single merchant."""

    url: str
    merchant_name: Optional[str] = None
    category: Optional[str] = None
    mcc_code: Optional[str] = None
    confidence: Optional[str] = None
    description: Optional[str] = None
    error: Optional[str] = None


class MCCBatchResponse(BaseModel):
    """Batch MCC classification response."""

    results: List[MCCResult]
