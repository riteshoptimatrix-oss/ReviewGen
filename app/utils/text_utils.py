import re
from typing import Optional

def clean_text(text: Optional[str]) -> Optional[str]:
    """
    Strips whitespace and newlines, collapsing multiple spaces into one.
    Returns None if the result is empty.
    """
    if text is None:
        return None
    
    # Remove zero-width spaces, non-breaking spaces, etc.
    text = text.replace('\xa0', ' ').replace('\u200b', '')
    
    # Collapse multiple whitespaces
    text = re.sub(r'\s+', ' ', text)
    
    text = text.strip()
    return text if text else None
