from typing import Optional,Dict, Any
from pydantic import BaseModel, Field

class TodoRequest(BaseModel):
    task: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Todo"
    )
    completed: bool = Field(default=False)
