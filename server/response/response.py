from pydantic import BaseModel
from typing import Optional, Dict


class Response(BaseModel):
    status: int
    message: str
    data: Optional[Dict] = None
