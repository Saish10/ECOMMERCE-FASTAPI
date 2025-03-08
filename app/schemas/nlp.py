from typing import List, Any
from pydantic import BaseModel


class QueryRequest(BaseModel):
    """Schema for handling natural language query requests"""

    query: str


class QueryResponse(BaseModel):
    """Schema for returning the generated SQL query and its execution result"""

    sql_query: str
    error: str
    result: List[Any]
