from pydantic import BaseModel
from typing import Optional, Any

class ExtractedValue(BaseModel):
    value: Optional[Any]
    source: Optional[str]
    confidence: float
