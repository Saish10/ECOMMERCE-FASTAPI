from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.nlp import QueryRequest, QueryResponse
from app.services.nlp import NLPQueryService
from app.utils.logger import logger

router = APIRouter(prefix="/nlp", tags=["NLP"])


@router.post("/generate-sql", response_model=QueryResponse)
async def generate_sql_query(
    request: QueryRequest, db: Session = Depends(get_db)
):
    """Generates and executes an SQL query from a natural language request."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        response = NLPQueryService.generate_and_execute_sql(request.query, db)

        if response.error:
            return QueryResponse(sql_query="", error=response.error, result=[])

        return response

    except Exception as e:
        logger.error("Error processing query: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error processing query: {str(e)}"
        ) from e
