import json
from fastapi import APIRouter, Depends, HTTPException
from google import genai
from google.genai import types
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.nlp import QueryRequest, QueryResponse
from app.services.nlp import NLPQueryService
from app.config import settings

router = APIRouter(prefix="/nlp", tags=["NLP"])


@router.post("/generate-sql", response_model=QueryResponse)
async def generate_sql_query(
    request: QueryRequest, db: Session = Depends(get_db)
):
    """Generates and executes an SQL query from a natural language request."""
    schema_str = NLPQueryService.get_database_schema(db)

    prompt = f"""
    You are an expert in SQL query generation. Given the following database schema:

    ### Database Schema:
    {schema_str}

    Convert the following natural language query into an SQL query:
    "{request.query}"

    ### Requirements:
    - Ensure the SQL query is syntactically correct.
    - Use only the tables and columns present in the provided schema.
    - Avoid unnecessary joins for optimal performance.
    - Validate that all referenced tables and columns exist in the schema.
    - If a table from the query is not found in the schema, return an error message specifying the missing table(s).
    - If a column from the query is not found in its respective table, return an error message specifying the missing column(s).
    - If the input query is unclear or ambiguous, return an appropriate validation error.
    - **Ensure text comparisons are case-insensitive.**
    - Use `ILIKE` for PostgreSQL.
    - Use `LOWER(column) = LOWER(value)` for MySQL/SQLite.

    ### Response Format:
    Return the response as a JSON object with:
    - `"sql_query"`: A string containing the generated SQL query (empty if an error occurs).
    - `"error"`: A string describing any validation issue (empty if no error occurs).

    ### Examples of Expected Errors:
    - If a table is missing: `"error": "The table 'orders' is not found in the schema."`
    - If a column is missing: `"error": "The column 'customer_id' does not exist in the 'orders' table."`
    - If both are missing: `"error": "The table 'orders' and column 'customer_id' do not exist in the schema."`

    Ensure the response is accurate, well-formatted, and follows best practices.
    """

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model=model,
            contents=contents,
        )

        # Remove triple quotes if they exist ("""json ... """)
        cleaned_text = (
            response.text.strip().removeprefix("```json").removesuffix("```")
        )
        response_json = json.loads(cleaned_text)
        sql_query = response_json.get("sql_query", "")
        error = response_json.get("error", "")
        results = NLPQueryService.execute_query(db, sql_query)

        return QueryResponse(sql_query=sql_query, error=error, result=results)

    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500, detail=f"Invalid JSON response from API: {str(e)}"
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating SQL query: {str(e)}"
        ) from e
