from pydantic import BaseModel, Field, validator
from typing import Optional, Union, Dict, Any
import time

class JarvisCommand(BaseModel):
    """
    Strict Definition of a Command entering the system.
    """
    text: str = Field(..., min_length=1, description="The raw text command from user")
    web_search: bool = Field(False, description="Whether to force web search")
    source: str = Field("unknown", description="Source of command (voice, text, api)")
    timestamp: float = Field(default_factory=time.time)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator('text')
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError("Command text cannot be empty")
        return v.strip()

class APIResponse(BaseModel):
    """
    Standardized Response format for API Clients.
    """
    status: str = "success"
    message: str
    data: Optional[Dict[str, Any]] = None
