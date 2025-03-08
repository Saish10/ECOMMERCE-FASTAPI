import json
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from fastapi import HTTPException

from google import genai
from google.genai import types
from app.config import settings
from app.schemas.nlp import QueryResponse
from app.utils.logger import logger


class NLPQueryService:
    """Handles SQL generation and execution logic."""

    @staticmethod
    def generate_and_execute_sql(
        natural_language_query: str, db: Session
    ) -> QueryResponse:
        """Generates SQL from natural language, validates, and executes it."""

        schema_str = NLPQueryService.get_database_schema(db)
        prompt = NLPQueryService.create_prompt(
            natural_language_query, schema_str
        )

        sql_query, error = NLPQueryService.call_gemini_api(prompt)

        if error:
            return QueryResponse(sql_query="", error=error, result=[])

        if NLPQueryService.is_query_dangerous(sql_query):
            return QueryResponse(
                sql_query="",
                error="Destructive SQL commands are not allowed.",
                result=[],
            )

        try:
            results = NLPQueryService.execute_query(db, sql_query)
            return QueryResponse(sql_query=sql_query, error="", result=results)
        except Exception as e:
            logger.error("SQL execution failed: %s", e, exc_info=True)
            return QueryResponse(
                sql_query="", error="Failed to execute SQL query.", result=[]
            )

    @staticmethod
    def create_prompt(natural_language_query: str, schema_str: str) -> str:
        """Creates the prompt for the AI model."""
        return f"""
        You are an expert in SQL query generation. Given the following database schema:

        ### Database Schema:
        {schema_str}

        Convert the following natural language query into an SQL query:
        "{natural_language_query}"

        ### Requirements:
        - Ensure the SQL query is syntactically correct.
        - Use only the tables and columns present in the provided schema.
        - Avoid unnecessary joins for optimal performance.
        - Validate that all referenced tables and columns exist in the schema.
        - If a table or column is missing, return an error message specifying which one.
        - If the input query is unclear, return a validation error.
        - **Ensure text comparisons are case-insensitive.**
        - Use `ILIKE` for PostgreSQL.
        - Use `LOWER(column) = LOWER(value)` for MySQL/SQLite.

        ### Response Format:
        Return the response as a JSON object with:
        - `"sql_query"`: A string containing the generated SQL query (empty if an error occurs).
        - `"error"`: A string describing any validation issue (empty if no error occurs).
        """

    @staticmethod
    def call_gemini_api(prompt: str) -> tuple[str, str]:
        """Calls the Gemini API and returns SQL query and any errors."""
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            model = "gemini-2.0-flash"
            contents = [
                types.Content(
                    role="user", parts=[types.Part.from_text(text=prompt)]
                )
            ]

            response = client.models.generate_content(
                model=model, contents=contents
            )

            # Ensure response is valid JSON
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            response_json = json.loads(response_text)
            return (
                response_json.get("sql_query", "").strip(),
                response_json.get("error", "").strip(),
            )

        except json.JSONDecodeError:
            logger.error("Invalid JSON response from Gemini API")
            return "", "Invalid response format from AI model."
        except Exception as e:
            logger.error("Error calling Gemini API: %s",e, exc_info=True)
            return "", "Error generating SQL query."

    @staticmethod
    def execute_query(db: Session, query: str) -> list[dict]:
        """Executes an SQL query and returns results."""
        try:
            result = db.execute(text(query)).fetchall()
            return [dict(row._mapping) for row in result]
        except SQLAlchemyError as e:
            logger.error("SQL execution error: %s", e, exc_info=True)
            raise HTTPException(
                status_code=400, detail="Error executing SQL query."
            ) from e

    @staticmethod
    def get_database_schema(db: Session) -> str:
        """Fetches database schema dynamically from PostgreSQL."""
        result: list[tuple[str, str]] = db.execute(
            text(
                """
                SELECT table_name, column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position;
                """
            )
        ).fetchall()

        schema: dict[str, list[str]] = {}
        for table, column in result:
            schema.setdefault(table, []).append(column)

        return "\n".join(
            [
                f"{table} ({', '.join(columns)})"
                for table, columns in schema.items()
            ]
        )

    @staticmethod
    def is_query_dangerous(query: str) -> bool:
        """Prevents execution of destructive SQL queries."""
        dangerous_keywords = [
            "DROP",
            "DELETE",
            "TRUNCATE",
            "ALTER",
            "UPDATE",
            "INSERT",
        ]
        return any(kw in query.upper() for kw in dangerous_keywords)
