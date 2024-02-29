from pydantic import BaseModel
from typing import Optional, Union, List, Dict


class Response(BaseModel):
    status: int
    message: str
    data: Optional[Union[List, Dict]] = None
