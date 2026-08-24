from pydantic import BaseModel, HttpUrl
from typing import Optional, Any
from app.schemas.common import ExtractedValue

class ResolveRequest(BaseModel):
    url: str

class BusinessData(BaseModel):
    input_url: str
    final_url: str
    business_name: Optional[str] = None
    raw_category: Optional[str] = None
    normalized_category: Optional[str] = None
    category_confidence: Optional[float] = None
    category_source: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None

class BulkResolveRequest(BaseModel):
    urls: list[str]

class BusinessMeta(BaseModel):
    status_code: int
    page_type: str
    duration_ms: int

class ErrorDetail(BaseModel):
    code: str
    message: str

class ResolveResponse(BaseModel):
    success: bool
    data: Optional[BusinessData] = None
    error: Optional[ErrorDetail] = None

